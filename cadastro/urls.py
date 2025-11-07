from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login, name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
]


