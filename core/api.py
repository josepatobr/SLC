from ninja import NinjaAPI
from home.api.api import router_home
from filmes.api.api import router_movies


api = NinjaAPI()
api.add_router("home/", router_home)
api.add_router("movies/", router_movies)
