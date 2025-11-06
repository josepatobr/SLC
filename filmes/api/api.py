from ninja import Router
from django.http import StreamingHttpResponse, HttpResponse
from django.conf import settings
import os

router = Router()


@router.get("video/")
def stream_video(request):
    path = os.path.join(settings.BASE_DIR, "media", "movies.mp4")
    file_size = os.path.getsize(path)
    range_header = request.headers.get('Range')

    if range_header:
        start, end = range_header.replace('bytes=', '').split('-')
        start = int(start)
        end = int(end) if end else file_size - 1
        length = end - start + 1

        def stream():
            with open(path, 'rb') as f:
                f.seek(start)
                yield f.read(length)

        response = StreamingHttpResponse(stream(), status=206, content_type='movies/mp4')
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        return response

    return HttpResponse(open(path, 'rb'), content_type='movies/mp4')