from ninja import Router
from dotenv import load_dotenv
from filmes.models import MovieView, Movies, Avaliacao
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from .schemas import RateIn

load_dotenv()
router_home = Router()


@router_home.post("CounterView/<int:movie_id>/")
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
    if already_viewed:
        return JsonResponse(
            {"status": "already_viewed", "watch_count": movie.watch_count}
        )
    else:
        return JsonResponse({"status": "unauthenticated"}, status=401)


@router_home.post("movie/{int:movie_id}/rate/", tags=["Avaliação"])
def movie_rate_ninja(request: HttpRequest, movie_id: int, payload: RateIn):
    movie = get_object_or_404(Movies, id=movie_id)
    user = request.user
    nota = payload.note

    if not 1 <= nota <= 5:
        return 400, {"message": "A nota deve ser um número entre 1 e 5."}

    try:
        with transaction.atomic():
            avaliacao, created = Avaliacao.objects.update_or_create(
                movie_rated=movie, user=user, defaults={"note": nota}
            )
        message = (
            "Avaliação registrada com sucesso!"
            if created
            else "Avaliação atualizada com sucesso!"
        )
        return 200, {"status": "ok", "message": message, "note": nota}

    except ValidationError as e:
        return 400, {"message": str(e)}
    except Exception:
        return 500, {"message": "Erro interno do servidor ao salvar avaliação."}
