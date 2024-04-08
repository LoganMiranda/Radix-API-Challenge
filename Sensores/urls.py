from django.urls import path, include
from . import views
from .views import LeituraSensor, Homesensores

app_name = 'Sensores'

urlpatterns = [
    path('api/Leitura_Json', views.dados_json, name='dados_json'),
    path('api/Leitura_CSV', views.dados_csv, name='dados_csv'),
    #path('leitura/<str:id_sensor>', LeituraSensor.as_view(), name='leitura_sensor'),
    path('leitura/<int:pk>', LeituraSensor.as_view(), name='leitura_sensor'),
    path('', Homesensores.as_view(),name='sensores'),
]