from payment.api.service import stripe_api
from filmes.api.api import router_movies
from upload.api import router_upload
from ninja import NinjaAPI


api = NinjaAPI()
api.add_router("movies/", router_movies)
api.add_router("upload/", router_upload)
api.add_router("payment/", stripe_api)
