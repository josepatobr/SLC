from django.shortcuts import render
import os
from dotenv import load_dotenv

load_dotenv()

def cadastro(request):
    return render(request, 'cadastro.html')

def login(request):
    return render(request, 'login.html')