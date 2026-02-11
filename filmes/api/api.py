from filmes.services.streaming import get_video_streaming_response
from filmes.models import Movies, Episode
from ninja import Router

router_movies = Router()
CHUNK_SIZE = 8192


@router_movies.get("video/{id}", url_name="stream-video")
def stream_video(request, id: int):
    video = None
    if movie := Movies.objects.filter(id=id).first():
        video = movie.file_movie
    elif episode := Episode.objects.filter(id=id).first():
        video = episode.file_episode

    else:
        return 404, {"detail": "Movie or episode not found."}
    if not video or video == "":
        return 404, {"detail": "Video not found."}

    return get_video_streaming_response(request, video)
