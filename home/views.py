from filmes.models import Movies, Avaliação
from django.shortcuts import render, get_object_or_404


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


def movie(request, id):
    movie = get_object_or_404(Movies, id=id)

    if request.method == 'POST':
        nota_enviada = request.POST.get('nota') 
        
        try:
            nova_avaliacao = Avaliação.objects.create(
                movie_rated=movie,
                note=int(nota_enviada) 
            )
        
        except ValueError:
            pass 
        except Exception as e:
            print(f"Erro ao salvar: {e}")

    return render(request, "movie.html", {"movie": movie})
