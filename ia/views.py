from django.shortcuts import render


def support_ia(request):
    return render(request, "ia.html")