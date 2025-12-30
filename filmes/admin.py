from django.contrib import admin
from .models import Movies, Gender, Serie, Episode



admin.site.register(Movies)
admin.site.register(Serie)
admin.site.register(Episode)
admin.site.register(Gender)