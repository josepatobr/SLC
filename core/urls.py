from django.contrib import admin
from django.urls import path, include
from core.api import api 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('/', include('cadastro.urls')),
    path('', include('home.urls'))

]
