from filmes.models import Movies, Avaliação
from django.shortcuts import render, get_object_or_404, redirect
from cadastro.models import CustomUser, CustomUserChangeForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest


def home(request):
    recommended_movies = Movies.objects.order_by("-watch_count")[:20]
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


@login_required
def movie(request, id):
    movie = get_object_or_404(Movies, id=id)
    user = request.user

    return render(
        request,
        "movie.html",
        {
            "movie": movie,
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
