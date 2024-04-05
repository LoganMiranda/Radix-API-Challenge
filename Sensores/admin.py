from django.contrib import admin
from .models import Sensor, Leitura

# Register your models here.
admin.site.register(Sensor)
admin.site.register(Leitura)
