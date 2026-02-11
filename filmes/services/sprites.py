import json, logging, os, boto3, math, subprocess
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
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            logger.error(f"FFprobe erro: {result.stderr}")
            return None

        data = json.loads(result.stdout)
        format_data = data.get("format", {})
        streams = data.get("streams", [])

        duration = float(format_data.get("duration", 0))
        if duration == 0 and streams:
            duration = float(streams[0].get("duration", 0))

        fps = 30.0
        if streams and "r_frame_rate" in streams[0]:
            rate = streams[0]["r_frame_rate"]
            if "/" in rate:
                num, den = rate.split("/")
                if float(den) > 0:
                    fps = float(num) / float(den)
            else:
                fps = float(rate)

        return {
            "duration": duration,
            "width": streams[0].get("width") if streams else None,
            "height": streams[0].get("height") if streams else None,
            "fps": fps,
        }
    except Exception as e:
        logger.error(f"Erro ao processar vídeo {video_url}: {e}")
        return None


def get_video_duration(video_url: str) -> float:
    metadata = get_video_metadata(video_url)
    return metadata.get("duration", 0) if metadata else 0


def process_video_to_hls(obj, input_path, temp_dir):
    duration = get_video_duration(input_path)

    if duration <= 0:
        return None

    output_dir = Path(temp_dir) / "hls"
    output_dir.mkdir(parents=True, exist_ok=True)
    hls_playlist_name = "playlist.m3u8"
    output_hls_path = output_dir / hls_playlist_name

    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-profile:v",
        "baseline",
        "-level",
        "3.0",
        "-s",
        "1280x720",
        "-start_number",
        "0",
        "-hls_time",
        "10",
        "-hls_list_size",
        "0",
        "-f",
        "hls",
        str(output_hls_path),
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.exception("Erro no FFmpeg: %s", e.stderr)
        return None

    relative_path = _upload_hls_files(obj, str(output_dir))

    return relative_path


def _upload_hls_files(obj, output_dir, model_type):
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

    s3_prefix = f"media/hls/{model_type}/{obj.id}"

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
        logger.error(f"Erro no upload para Cloudflare: {e}")
        return None


def generate_video_sprites(obj, input_path, temp_dir):
    interval = 10
    thumb_width = 160
    columns = 5

    from .sprites import get_video_duration

    duration = get_video_duration(input_path)

    if duration <= 0:
        return

    total_thumbs = math.ceil(duration / interval)
    rows = math.ceil(total_thumbs / columns)

    sprite_image_path = os.path.join(temp_dir, "sprite.jpg")
    vtt_path = os.path.join(temp_dir, "thumbnails.vtt")

    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-vf",
        f"fps=1/{interval},scale={thumb_width}:-1,tile={columns}x{rows}",
        "-q:v",
        "5",
        sprite_image_path,
        "-y",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)

        with open(vtt_path, "w") as f:
            f.write("WEBVTT\n\n")

            for i in range(total_thumbs):
                start = i * interval
                end = (i + 1) * interval

                t_start = f"{int(start // 3600):02}:{int((start % 3600) // 60):02}:{int(start % 60):02}.000"
                t_end = f"{int(end // 3600):02}:{int((end % 3600) // 60):02}:{int(end % 60):02}.000"

                x = (i % columns) * thumb_width
                y = (i // columns) * int(thumb_width * 9 / 16)

                f.write(f"{t_start} --> {t_end}\n")
                f.write(f"sprite.jpg#xywh={x},{y},{thumb_width},90\n\n")

    except subprocess.CalledProcessError as e:
        logger.error(f"Erro no FFmpeg ao gerar sprites: {e.stderr}")
        raise e


"""
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
"""
