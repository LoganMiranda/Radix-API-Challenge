from django.urls import path, include
from . import views

app_name = 'Sensores'

urlpatterns = [
    path('api/Leitura_Json', views.dados_json, name='dados_json'),
    path('api/Leitura_CSV', views.dados_csv, name='dados_csv'),
]