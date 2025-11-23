from filmes.models import Movies, MoviesWatched, Serie, EpisodeWatched
from django.shortcuts import render, get_object_or_404, redirect
from cadastro.models import CustomUser, CustomUserChangeForm
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_authenticated:
        history_entries = MoviesWatched.objects.filter(user=request.user).order_by(
            "-watched_at"
        )
        movies_watched_objects = [entry.movie_watched for entry in history_entries]
    else:
        movies_watched_objects = []

    if request.user.is_authenticated:
        history_serie_entries = EpisodeWatched.objects.filter(
            user=request.user
        ).order_by("-watched_at")
        serie_watched_objects = [
            entry.episode_watched for entry in history_serie_entries
        ]
    else:
        serie_watched_objects = []

    recommended_movies = Movies.objects.order_by("-watch_count")[:20]
    romance_movies = Movies.objects.filter(gender__genders="ROMANCE")
    action_movies = Movies.objects.filter(gender__genders="ACTION")
    series = Serie.objects.all()

    return render(
        request,
        "home.html",
        {
            "series_watched": serie_watched_objects,
            "movies_watched": movies_watched_objects,
            "recommended_movies": recommended_movies,
            "serie": series,
            "romance_movies": romance_movies,
            "action_movies": action_movies,
        },
    )


@login_required
def movie(request, id):
    movie = get_object_or_404(Movies, id=id)

    return render(
        request,
        "movie.html",
        {
            "movie": movie,
        },
    )


@login_required
def serie(request, id):
    serie = get_object_or_404(Serie, id=id)
    seasons = serie.seasons.all().prefetch_related("episodes")

    return render(
        request,
        "serie.html",
        {
            "serie": serie,
            "seasons": seasons,
        },
    )


def profile(request, id):
    user = CustomUser.objects.get(id=id)
    return render(request, "profile.html", {"user": user})


def profile_edit(request, id):
    user_to_edit = get_object_or_404(CustomUser, id=id)

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user_to_edit)
        if form.is_valid():
            form.save()
            return redirect("profile", id=user_to_edit.id)
    else:
        form = CustomUserChangeForm(instance=user_to_edit)
    return render(request, "profile_edit.html", {"form": form, "user": user_to_edit})
