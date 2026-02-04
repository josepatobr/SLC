from ia.api.schemas import QuestionSchema
from django.conf import settings
from ninja import Router
import openai


router_ia = Router()


@router_ia.post("chat/")
def ia_detalhes(request, data: QuestionSchema):
    client = openai.Client(api_key=settings.SECRET_KEY_OPENIA)

    ia_mindset = """Você é uma assistente virtual gentil, educada, direta e especializada exclusivamente em cinema e séries. 

                    Regras de comportamento:
                    1. Responda com entusiasmo mas no foco naquilo que foi perguntado sobre qualquer filme, série, diretor ou premiação.
                    2. Se o usuário fizer uma pergunta que NÃO seja sobre filmes e series, peça desculpas de forma muito educada. 
                    3. Use uma 'desculpa' charmosa, dizendo que você vive tanto no mundo das telas e dos roteiros que acaba se esquecendo de outros assuntos do mundo real.
                    4. sempre responde a pergunte dele.
                    5. não foge da pergunta dele, sempre responde o que ele perguntou.
                    6. responde do jeito mais direto possivel mas mantendo a educação.
                    7. caso ele pergunte uma indicação de um filme ou serie, fale o top 3 de cada genero.
                    8. caso ele pergunte sobre um filme especifico, fale o nome do diretor e do ator principal
                 """
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": ia_mindset},
                {"role": "user", "content": data.question},
            ],
        )

        texto_resposta = response.choices[0].message.content
        return {"response": texto_resposta}

    except Exception as e:
        return {"response": f"erro, falha no sistema: {str(e)}"}