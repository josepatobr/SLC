from ninja import NinjaAPI
from cadastro.api.api import router_cadastro
from home.api.api import router_home
from filmes.api.api import router_movies


api = NinjaAPI(urls_namespace='main_api')
api.add_router("auth/", router_cadastro)
api.add_router("home/", router_home)
api.add_router("movies/", router_movies)

