from django.shortcuts import render
from django.conf import settings
import openai

def support_ia(request):
    question_text = ""
   
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

    if request.method == "POST":
        user_question = request.POST.get("question")

        if user_question:
            try:
                client = openai.Client(api_key=settings.SECRET_KEY_OPENIA)
                response = client.chat.completions.create(
                     model="gpt-5-nano",
                    messages=[
                        {"role": "system", "content": ia_mindset},
                        {"role": "user", "content": user_question},
                    ]
                )

                question_text = response.choices[0].message.content
            except Exception as e:
                question_text = "Cena cortada! Tive um erro técnico. Tente novamente."
                print(f"Erro: {e}")

    return render(request, "ia.html", {"response": question_text})