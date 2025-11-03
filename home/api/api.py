from ninja import Router
from dotenv import load_dotenv
from filmes.models import MovieView, Movies
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

load_dotenv()
router = Router()


@router.post("CounterView/<int:movie_id>/")
def CounterView(request, movie_id):
    movie = get_object_or_404(Movies, id=movie_id)

    if request.user.is_authenticated:
        already_viewed = MovieView.objects.filter(
            user=request.user, movie=movie
        ).exists()
        if not already_viewed:
            movie.view_counter()
            MovieView.objects.create(user=request.user, movie=movie)
        return JsonResponse({"status": "ok", "watch_count": movie.watch_count})
