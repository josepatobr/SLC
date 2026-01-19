import json, logging, os, boto3, math, subprocess, shutil
from filmes.models import Video, VideoSprite
from filmes.utils import get_threads_count
from django.core.files import File
from django.conf import settings
from pathlib import Path


THUMB_WIDTH = 320
SPRITE_INTERVAL = 10
MAX_SPRITE_WIDTH = 1920
MAX_SPRITE_HEIGHT = 8000


logger = logging.getLogger(__name__)


def get_video_metadata(video_url: str):
    if not video_url:
        return None

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=width,height,duration,r_frame_rate",
        "-of",
        "json",
        video_url,
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            logger.error(f"FFprobe erro: {result.stderr}")
            return None

        data = json.loads(result.stdout)

        duration = float(data.get("format", {}).get("duration", 0))
        streams = data.get("streams", [])

        if duration == 0 and streams:
            duration = float(streams[0].get("duration", 0))

        return {
            "duration": duration,
            "width": streams[0].get("width") if streams else None,
            "height": streams[0].get("height") if streams else None,
        }
    except Exception as e:
        logger.error(f"Erro ao processar vídeo {video_url}: {e}")
        return None


def get_video_duration(video_url: str) -> float:
    metadata = get_video_metadata(video_url)
    if metadata:
        return metadata.get("duration", 0)
    return 0


def _build_ffmpeg_command(input_url, output_dir, valid_resolutions, fps):
    gop_size = int(fps) * 2

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        input_url,
    ]

    filter_complex = []
    map_configs = []

    for i, res in enumerate(valid_resolutions):
        width = res["width"]
        height = res["height"]
        bitrate = res["bitrate"]
        bufsize = res["bufsize"]

        filter_complex.append(
            f"[0:v]scale=w={width}:h={height}:force_original_aspect_ratio=decrease[v{i}]"
        )

        map_configs.extend(
            [
                "-map",
                f"[v{i}]",
                "-map",
                "0:a",
                f"-c:v:{i}",
                "libx264",
                f"-b:v:{i}",
                bitrate,
                f"-maxrate:v:{i}",
                bitrate,
                f"-bufsize:v:{i}",
                bufsize,
                f"-c:a:{i}",
                "aac",
                f"-b:a:{i}",
                "128k",
            ]
        )

    cmd.extend(["-filter_complex", ";".join(filter_complex)])
    cmd.extend(map_configs)

    cmd.extend(
        [
            "-preset",
            "veryfast",
            "-g",
            str(gop_size),
            "-sc_threshold",
            "0",
            "-f",
            "hls",
            "-hls_time",
            "6",
            "-hls_playlist_type",
            "vod",
            "-hls_segment_filename",
            f"{output_dir}/v%v/segment_%03d.ts",
            "-master_pl_name",
            "master.m3u8",
            "-var_stream_map",
            " ".join([f"v:{i},a:{i}" for i in range(len(valid_resolutions))]),
            f"{output_dir}/v%v/playlist.m3u8",
        ]
    )

    return cmd


def process_video_to_hls(video_instance: Video, temp_dir: str):
    metadata = get_video_metadata(video_instance)
    if not metadata:
        video_instance.status = Video.Status.FAILED
        video_instance.processing_error = "Could not probe video metadata."
        video_instance.save(update_fields=["status", "processing_error"])
        return

    output_dir = Path(temp_dir) / "hls"
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = _build_ffmpeg_command(
        video_instance,
        output_dir,
        metadata.get("fps", 30.0),
    )

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.exception("FFmpeg error: %s", e.stderr, exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        video_instance.status = Video.Status.FAILED
        video_instance.processing_error = f"FFmpeg failed: {e.stderr}"
        video_instance.save(update_fields=["status", "processing_error"])
        return
    except Exception as e:
        logger.exception("Unexpected error running FFmpeg", exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        video_instance.status = Video.Status.FAILED
        video_instance.processing_error = f"Error running FFmpeg: {e}"
        video_instance.save(update_fields=["status", "processing_error"])
        return

    relative_path = _upload_hls_files(video_instance, output_dir)
    if not relative_path:
        shutil.rmtree(temp_dir, ignore_errors=True)
        video_instance.status = Video.Status.FAILED
        video_instance.processing_error = "Failed to upload files."
        video_instance.save(update_fields=["status", "processing_error"])
        return

    video_instance.hls_playlist.name = relative_path
    video_instance.status = Video.Status.COMPLETED
    video_instance.processing_error = ""
    video_instance.save(update_fields=["status", "hls_playlist", "processing_error"])
    shutil.rmtree(temp_dir, ignore_errors=True)


def _upload_hls_files(video_instance: Video, output_dir):
    if not os.path.exists(output_dir):
        return None

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name="auto",
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    s3_prefix = f"media/hls/{video_instance.id}"

    master_playlist_path = None

    try:
        for root, dirs, files in os.walk(output_dir):
            for filename in files:
                local_path = os.path.join(root, filename)
                s3_key = f"{s3_prefix}/{filename}"

                if filename.endswith(".m3u8"):
                    content_type = "application/vnd.apple.mpegurl"
                    master_playlist_path = s3_key
                elif filename.endswith(".ts"):
                    content_type = "video/MP2T"
                else:
                    content_type = "application/octet-stream"

                with open(local_path, "rb") as data:
                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=s3_key,
                        Body=data,
                        ContentType=content_type,
                    )

        return master_playlist_path

    except Exception as e:
        print(f"Erro no upload para Cloudflare: {e}")
        return None


def generate_video_sprites(video: Video, temp_dir: Path):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name="auto",
    )

    if video.status != Video.Status.PROCESSING:
        video.status = Video.Status.PROCESSING
        video.save(update_fields=["status"])

    current_sprites = video.get_sprites()
    if current_sprites.count() > 0:
        current_sprites.delete()

    video_url = s3_client(video.source_file.url)
    duration = get_video_duration(video_url)
    if duration <= 0:
        logger.warning("Video duration is 0 or less. Cannot generate sprites.")
        return

    columns = math.floor(MAX_SPRITE_WIDTH / THUMB_WIDTH)
    thumb_height = int(THUMB_WIDTH * 9 / 16)
    max_rows = math.floor(MAX_SPRITE_HEIGHT / thumb_height)
    thumbs_per_sprite = columns * max_rows
    chunk_duration = thumbs_per_sprite * SPRITE_INTERVAL

    output_dir = Path(temp_dir) / "sprites"
    output_dir.mkdir(parents=True, exist_ok=True)

    total_chunks = math.ceil(duration / chunk_duration)

    for i in range(total_chunks):
        start_time = i * chunk_duration
        end_time = min((i + 1) * chunk_duration, duration)

        actual_chunk_duration = end_time - start_time
        expected_frames = math.ceil(actual_chunk_duration / SPRITE_INTERVAL)
        current_rows = math.ceil(expected_frames / columns)

        sprite_filename = f"sprite_{i}.jpg"
        output_path = output_dir / sprite_filename

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-threads",
            str(get_threads_count()),
            "-y",
            "-ss",
            str(start_time),
            "-t",
            str(actual_chunk_duration),
            "-i",
            str(video_url),
            "-vf",
            f"fps=1/{SPRITE_INTERVAL},scale={THUMB_WIDTH}:-1,format=yuv420p,tile={columns}x{current_rows}",
            "-q:v",
            "5",
            str(output_path),
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.exception("FFmpeg error: %s", e.stderr, exc_info=e)
            shutil.rmtree(temp_dir, ignore_errors=True)
            video.status = Video.Status.FAILED
            video.processing_error = f"FFmpeg failed to generate sprites: {e.stderr}"
            video.save(update_fields=["status", "processing_error"])
            return

        frame_height = int(THUMB_WIDTH * 9 / 16)
        with Path.open(output_path, "rb") as f:
            sprite_obj = VideoSprite.objects.create(
                video=video,
                start_time=int(start_time),
                end_time=int(end_time),
                interval=SPRITE_INTERVAL,
                frame_width=THUMB_WIDTH,
                frame_height=frame_height,
                columns=columns,
                rows=current_rows,
            )

            django_file = File(f)
            sprite_obj.image.save(sprite_filename, django_file, save=True)
        Path.unlink(output_path)

    video.status = Video.Status.COMPLETED
    video.processing_error = ""
    video.save(update_fields=["status", "processing_error"])
    shutil.rmtree(temp_dir, ignore_errors=True)


def get_video_tracks_metadata(video_url: str):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name="auto",
    )
    command = [
        "ffprobe",
        "-hide_banner",
        "-v",
        "error",
        "-show_entries",
        "stream=index,codec_type,r_frame_rate,width,height:stream_tags=language,title",
        "-of",
        "json",
        s3_client(video_url),
    ]

    try:
        res = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(res.stdout)

        streams = data.get("streams", [])
        audio_streams = []
        subtitle_streams = []

        for s in streams:
            idx = s["index"]
            codec = s["codec_type"]
            tags = s.get("tags", {})
            lang = tags.get("language", "und")
            title = tags.get("title", ("Track %s") % idx)

            track_info = {
                "index": idx,
                "language": lang,
                "label": title,
            }

            if codec == "audio":
                audio_streams.append(track_info)
            elif codec == "subtitle":
                subtitle_streams.append(track_info)
    except Exception as e:
        logger.exception("Error parsing FFprobe output", exc_info=e)
        return None
    else:
        return {"audio": audio_streams, "subtitle": subtitle_streams}

