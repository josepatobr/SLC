from filmes.urls import normalize_local_s3_url_to_service
from concurrent.futures import ThreadPoolExecutor
from filmes.utils import get_source_file_path
from filmes.utils import get_threads_count
import logging, subprocess, os, shutil
from typing import TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from filmes.models import Movies, Episode

logger = logging.getLogger(__name__)


def _build_ffmpeg_command(
    input_url: str,
    output_dir: Path,
    resolutions: list[dict],
    fps: float,
) -> list[str]:
    gop_size = str(int(fps * 2))
    split_count = len(resolutions)

    outputs = "".join([f"[v{i}]" for i in range(split_count)])
    filter_complex = f"[0:v]split={split_count}{outputs};"

    for i, res in enumerate(resolutions):
        filter_complex += (
            f"[v{i}]scale=w={res['width']}:h={res['height']}:force_original_aspect_ratio=decrease,"
            f"pad=ceil(iw/2)*2:ceil(ih/2)*2:(ow-iw)/2:(oh-ih)/2[v{i}out];"
        )

    filter_complex = filter_complex.rstrip(";")

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        input_url,
        "-filter_complex",
        filter_complex,
        "-preset",
        "medium",
        "-an",
        "-sn",
    ]

    var_stream_map = []
    for i, res in enumerate(resolutions):
        cmd.extend(
            [
    
                "-map",
                f"[v{i}out]",
                f"-c:v:{i}",
                "libx264",
                f"-crf:{i}",
                res["crf"],
                f"-maxrate:v:{i}",
                res["maxrate"],
                f"-bufsize:v:{i}",
                res["bufsize"],
                "-g",
                gop_size,
                "-keyint_min",
                gop_size,
                "-sc_threshold",
                "0",
            ],
        )
        var_stream_map.append(f"v:{i}")

    cmd.extend(
        [
            "-threads",
            str(get_threads_count()),
            "-f",
            "hls",
            "-hls_time",
            "6",
            "-hls_playlist_type",
            "vod",
            "-hls_flags",
            "independent_segments",
            "-master_pl_name",
            "master.m3u8",
            "-hls_segment_filename",
            str(output_dir / "v%v/segment_%03d.ts"),
            "-var_stream_map",
            " ".join(var_stream_map),
            str(output_dir / "v%v/prog.m3u8"),
        ],
    )
    return cmd


def _get_target_resolutions(original_height: int) -> list[dict]:
    all_resolutions = [
        {
            "name": "1080p",
            "width": 1920,
            "height": 1080,
            "crf": "22",
            "maxrate": "6400k",
            "bufsize": "12000k",
        },
        {
            "name": "720p",
            "width": 1280,
            "height": 720,
            "crf": "23",
            "maxrate": "3300k",
            "bufsize": "6000k",
        },
        {
            "name": "480p",
            "width": 854,
            "height": 480,
            "crf": "24",
            "maxrate": "1650k",
            "bufsize": "3000k",
        },
    ]
    valid = [res for res in all_resolutions if res["height"] <= original_height + 10]
    return valid or [all_resolutions[-1]]


def _upload_hls_files(instance: "Movies | Episode", output_dir: Path) -> str | None:  
    if not instance:
        return None  
    
    
    hls_storage = instance.hls_playlist.storage
    bucket_name = hls_storage.bucket_name
    s3_client = hls_storage.connection.meta.client

    relative_path = get_source_file_path(instance, "master.m3u8")
    s3_base_dir = str(Path(relative_path).parent)
  

    files_to_upload = []
    for root, __, files in os.walk(output_dir):
        for file in files:
            local_path = Path(root) / file
            rel_path = local_path.relative_to(output_dir)
            s3_key = f"{s3_base_dir}/{rel_path}"

            content_type = "application/octet-stream"
            if file.endswith(".m3u8"):
                content_type = "application/vnd.apple.mpegurl"
            elif file.endswith(".ts"):
                content_type = "video/MP2T"

            files_to_upload.append(
                (str(local_path), bucket_name, s3_key, content_type),
            )

    def upload_single_file(args):
        local, bucket, key, c_type = args
        s3_client.upload_file(local, bucket, key, ExtraArgs={"ContentType": c_type})

    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(upload_single_file, files_to_upload)
    except Exception as e:
        logger.exception("Error uploading HLS files", exc_info=e)
        return None
    else:
        return relative_path


def process_video_to_hls(instance: "Movies | Episode", temp_dir: str):
    input_url = normalize_local_s3_url_to_service(instance.source_file.url)

    output_dir = Path(temp_dir) / "hls"
    output_dir.mkdir(parents=True, exist_ok=True)

    valid_resolutions = _get_target_resolutions(getattr["height"])

    logger.info(
        "Video %s: Generating resolutions: %s",
        instance.id,
        [r["name"] for r in valid_resolutions],
    )

    cmd = _build_ffmpeg_command(
        input_url,
        output_dir,
        valid_resolutions,
        getattr("fps", 30.0),
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
        instance.save(update_fields=["status", "processing_error"])
        return
    except Exception as e:
        logger.exception("Unexpected error running FFmpeg", exc_info=e)
        shutil.rmtree(temp_dir, ignore_errors=True)
        instance.save(update_fields=["status", "processing_error"])
        return

    relative_path = _upload_hls_files(instance, output_dir)
    if not relative_path:
        shutil.rmtree(temp_dir, ignore_errors=True)
        instance.save(update_fields=["status", "processing_error"])
        return

    instance.hls_playlist.name = relative_path
    instance.save(update_fields=["status", "hls_playlist", "processing_error"])
    shutil.rmtree(temp_dir, ignore_errors=True)