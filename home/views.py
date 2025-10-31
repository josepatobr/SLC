from filmes.models import Movies
from django.shortcuts import render, get_object_or_404


def home(request):
    #recommended_movies = Movies.objects.order_by("-watch_count")[:20]
    recommended_movies = Movies.objects.all()
    romance_movies = Movies.objects.filter(gender__genders="ROMANCE")
    action_movies = Movies.objects.filter(gender__genders="ACTION")

    return render(
        request,
        "home.html",
        {
            "recommended_movies": recommended_movies,
            "romance_movies": romance_movies,
            "action_movies": action_movies,
        },
    )


def movie(request, id):
    movie = get_object_or_404(Movies, id=id)
    return render(request, "movie.html", {"movie": movie})
