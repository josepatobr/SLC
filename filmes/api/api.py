from ninja import Router
from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
import os
from django.http import FileResponse
router_movies = Router()
CHUNK_SIZE = 8192


@router_movies.get("video/{id}")
def stream_video(request, id: int):
    path = os.path.join(settings.BASE_DIR, "media", f"video_{id}.mp4")

    if not os.path.exists(path):
        return HttpResponse("Arquivo não encontrado.", status=404)

    file_size = os.path.getsize(path)
    range_header = request.headers.get("Range")

    if range_header:
        try:
            start_str, end_str = range_header.replace("bytes=", "").split("-")
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1
        except ValueError:
            return HttpResponse("Range Header inválido.", status=400)
        
        if start > end:
            return HttpResponse("Range inválido: start maior que end.", status=416)

        start = max(0, start)
        end = min(file_size - 1, end)
        length = end - start + 1

        def stream_chunked():
            bytes_read = 0
            with open(path, "rb") as f:
                f.seek(start)
                while bytes_read < length:
                    read_size = min(CHUNK_SIZE, length - bytes_read)
                    data = f.read(read_size)
                    if not data:
                        break
                    bytes_read += len(data)
                    yield data

        response = StreamingHttpResponse(
            stream_chunked(), status=206, content_type="video/mp4"
        )
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        response["Accept-Ranges"] = "bytes"
        response["Content-Length"] = str(length)
        return response

    response = FileResponse(open(path, "rb"), content_type="video/mp4", status=200)
    response["Content-Length"] = str(file_size)
    response["Accept-Ranges"] = "bytes"
    return response
