from ninja import Router
from dotenv import load_dotenv

load_dotenv()
router = Router()


@router.post("home/")
def cadastro(request):
    return None
