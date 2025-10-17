from ninja import NinjaAPI
from cadastro.api.api import router as cadastro_router 

api = NinjaAPI()
api.add_router("auth/", cadastro_router)


