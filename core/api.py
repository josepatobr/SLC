from filmes.api.api import router_movies
from home.api.api import router_home
from upload.api import router_upload
from ninja import NinjaAPI


api = NinjaAPI()
api.add_router("home/", router_home)
api.add_router("movies/", router_movies)
api.add_router("upload/", router_upload)
