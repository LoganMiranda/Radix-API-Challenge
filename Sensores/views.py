from django.views.generic import TemplateView, ListView, DetailView
from .models import Sensor, Leitura
import csv, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dateutil import parser
# Create your views here.

@csrf_exempt
def dados_json(request):

    if request.method == 'POST':
        dados_sensor = json.loads(request.body)
        equipmentId = dados_sensor["equipmentId"]

        #verifica se sensor ja existe no BD
        if Sensor.sensor_existe(equipmentId) == True:
                mensagem = "Sensor ja existe"
        
        else:

            #Construtor padrão do Django. Instancia novo objeto da classe Sensor e salva no BD.
            name = 'testex'+ equipmentId 
            sensor = Sensor.objects.create(id_sensor = equipmentId, nome = name )
            mensagem = 'sensor nao existia, mas foi criado e inserido no BD com sucesso'
            
    sensor = Sensor.objects.get(id_sensor = equipmentId)
    timestamp = parser.parse(dados_sensor['timestamp'])
            
    try:
        sensor.criar_Leitura(timestamp, dados_sensor['value']) 
    except:
        mensagem = 'Nao pode existir mais de uma mesma leitura para um mesmo sensor em um mesmo timestamp'
            
    return JsonResponse({"mensagem":mensagem})


@csrf_exempt
def dados_csv(request):

    if request.method == 'POST':
        arquivo_csv = request.body.decode('utf-8').splitlines()
        arquivo_csv = list(csv.reader(arquivo_csv))
        
        #acha posição do cabeçalho do arquivo_csv e soma 1, pois queremos os valores e nao o proprio cabeçalho
        posicao_cabecalho = arquivo_csv.index(['equipmentId;timestamp;value']) + 1
        
        for linha in arquivo_csv[posicao_cabecalho:]:
            
            #condiçao identificada que, apos o cabeçalho, a lista vazia representa o fim do arquivo
            if linha == []:
                break
            
            else:
                equipmentId, timestamp, value = linha[0].split(';')
                
                if Sensor.sensor_existe(equipmentId) == False:
                    name = 'testex'+ equipmentId
                    sensor = Sensor.objects.create(id_sensor = equipmentId, nome = name)
                
                else:
                    sensor = Sensor.objects.get(id_sensor = equipmentId)
                timestamp = parser.parse(timestamp)
                
                try:
                    sensor.criar_Leitura(timestamp, value)
                
                except:
                    print('Nao pode existir mais de uma mesma leitura para um mesmo sensor em um mesmo timestamp')

        mensagem = 'recebi o arquivo csv com sucesso'
        return JsonResponse({"mensagem":mensagem})


class Homepage(TemplateView):
    template_name = 'homepage.html'
    
    #model = Leitura