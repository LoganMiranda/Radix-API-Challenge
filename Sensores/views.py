from django.shortcuts import render
from .models import Sensor, Leitura
import csv, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def dados_json(request):

    if request.method == 'POST':
        dados_sensor = json.loads(request.body)
        equipmentId = dados_sensor["equipmentId"]
        name = 'testex'+ equipmentId
        
        try:
            if Sensor.objects.get(id_sensor = equipmentId):
                mensagem = "Sensor ja existe"
                return JsonResponse({"mensagem":mensagem})
        
        except:

            #instancia novo objeto da classe Sensor
            sensor = Sensor(id_sensor = equipmentId, nome = name )
            #salva no BD
            sensor.save()

            mensagem = 'sensor nao existia, mas foi criado e inserido no BD com sucesso'
            return JsonResponse({"mensagem":mensagem})
        