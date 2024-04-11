from django.views.generic import TemplateView, ListView, DetailView
from .models import Sensor, Leitura
import csv, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dateutil import parser
from django.utils import timezone
from datetime import timedelta
import matplotlib.pyplot as plt
import io, base64
import random
from time import sleep
# Create your views here.

@csrf_exempt
def dados_json(request):

    if request.method != 'POST':
        return JsonResponse({"erro": 'API só recebe requisições do tipo POST'})

    dados_sensor = json.loads(request.body)
    
    try:
        equipmentId = dados_sensor["equipmentId"]
    except:
        return JsonResponse({"erro":" chave 'equipmentId' nao esta no Json. Deve ser exatamente 'equipmentId'."})
    
    if len(str(equipmentId)) > 8:
        return JsonResponse({"erro":"equipmentId tem mais de 8 caracteres."})
    
    try:
        timestamp = dados_sensor['timestamp']
    except:
        return JsonResponse({"erro": "chave 'timestamp' nao esta no Json. Deve ser exatamente 'timestamp'."})
    
    try:
        timestamp_recebido = timestamp
        timestamp = parser.parse(dados_sensor['timestamp'])
    except:
        return JsonResponse({"codigo": 400, "mensagem": f" '{timestamp_recebido}' nao esta no formato esperado(timestamp with timezone)."})
    
    try:
        value = dados_sensor["value"]
    except:
        return JsonResponse({"erro":" chave 'value' nao esta no Json. Deve ser exatamente 'value'."})

    try:
        value = float(value)
    except:
        return JsonResponse({"codigo": 400, "mensagem": f" '{value}' nao é do tipo float."})



    #verifica se sensor ja existe no BD
    if Sensor.sensor_existe(equipmentId) == False:

        #Construtor padrão do Django. Instancia novo objeto da classe Sensor e salva no BD.
        name = 'testex'+ equipmentId 
        sensor = Sensor.objects.create(id_sensor = equipmentId, nome = name )
            
    sensor = Sensor.objects.get(id_sensor = equipmentId)

    try:
        sensor.criar_Leitura(timestamp, value) 
    except:
        return JsonResponse({"codigo": 400, "mensagem": f"Ja existe uma leitura associada a:{equipmentId, timestamp_recebido}. Um mesmo sensor nao pode ter mais de uma leitura em um mesmo instante de tempo."})
            
    return JsonResponse({"codigo":201, "mensagem":"Json recebido com sucesso"})





@csrf_exempt
def dados_csv(request):

    if request.method != 'POST':
        return JsonResponse({"erros": 'API só recebe requisições do tipo POST'})
    
    erros = []
    
    try:
        arquivo = request.body.decode('utf-8').splitlines()
    except:
        erros.append({"codigo": 400, "mensagem": 'arquivo veio criptografado. Nao é do tipo csv'})
        return JsonResponse({"erros": erros})
    
    content_type = arquivo[2].split(':')
    if content_type[1] != ' text/csv':
        erros.append({"codigo": 400, "mensagem": "arquivo enviado não é do tipo csv"})
        return JsonResponse({"erros": erros})
    
    arquivo_csv = list(csv.reader(arquivo))
    
    #acha posição do cabeçalho do arquivo_csv e soma 1, pois queremos os valores e nao o proprio cabeçalho
    try:
        posicao_cabecalho = arquivo_csv.index(['equipmentId;timestamp;value']) + 1
    
    except:
        erros.append({"codigo": 400, "mensagem": "header do csv, ou seja, os nomes das colunas estão errados ou na ordem incorreta"})
        return JsonResponse({"erros": erros})
    
    for linha in arquivo_csv[posicao_cabecalho:]:
        
        #condiçao identificada que, apos o cabeçalho, a lista vazia representa o fim do arquivo
        if linha == []:
            break
            
        else:
            equipmentId, timestamp, value = linha[0].split(';')

            if len(str(equipmentId)) > 8:
                erros.append({"codigo": 400, "mensagem": f"{equipmentId} tem mais que 8 caracteres."})            
            
            try:
                timestamp_recebido = timestamp
                timestamp = parser.parse(timestamp)
            except:
                erros.append({"codigo": 400, "mensagem": f" '{timestamp_recebido}' nao esta no formato esperado(timestamp with timezone)."})
            
            try:
                value = float(value)
            except:
                erros.append({"codigo": 400, "mensagem": f"value = '{value}' não é do tipo float."})

            if Sensor.sensor_existe(equipmentId) == False:
                name = 'testex'+ equipmentId
                sensor = Sensor.objects.create(id_sensor = equipmentId, nome = name)
            
            else:
                sensor = Sensor.objects.get(id_sensor = equipmentId)
            
            try:
                sensor.criar_Leitura(timestamp, value)
            
            except:
                erros.append({"codigo": 400, "mensagem": f"Ja existe uma leitura associada a:{equipmentId, timestamp_recebido}. Um mesmo sensor nao pode ter mais de uma leitura em um mesmo instante de tempo."})
    
    
    mensagem = 'recebi o arquivo csv com sucesso'
    return JsonResponse({"mensagem": mensagem, "erros": erros})
        




class Homesensores(ListView):
    template_name = 'sensores.html'
    model = Sensor

    


class LeituraSensor(DetailView):
    template_name = 'detalhes_sensor.html'
    model = Sensor

    def constroi_grafico(self, tempo):
        
        sensor = self.get_object()
        agora = timezone.now().astimezone(timezone.get_current_timezone())
        limite_tempo = agora - timedelta(hours=tempo)
        leituras = sensor.leitura.filter(timestamp__gte=limite_tempo)
        
        x, y = list(), list()
        for leitura in leituras:
            x.append(str(leitura.timestamp)[11:16])
            y.append(leitura.valor)
        
        plt.plot(x, y)
        plt.xlabel('Timestamp')
        plt.ylabel('Valor')
        plt.title('Gráfico de Leituras')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        grafico = base64.b64encode(image_png).decode('utf-8')
        
        return grafico

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #sensor = self.get_object()
        
        ''' !!!!!!!!TESTE!!!!!!!
        for c in range(0,10):
            try:
                sleep(30)
                agora = timezone.now().astimezone(timezone.get_current_timezone())
                valor = round(random.uniform(0,100),2)
                sensor.criar_Leitura(agora, valor )
            except:
                print('erro')'''
        
        #obtemos o parametro de url que esta sendo passado            
        tempo = int(self.request.GET.get('horas'))
        #geramos o grafico em uma funçao propria para isso, criada acima 
        grafico = self.constroi_grafico(tempo)
        #adicionamos o grafico gerado ao dicionario context, para podermos utiliza-lo no nosso template
        context['grafico'] = grafico
    
        return context
    

class PesquisaSensor(ListView):
    template_name = 'pesquisa_sensor.html'
    model = Sensor

    def get_queryset(self):
        
        #parametro 'query' porque no pesquisa_sensor.html o formulario foi criado  com esse parametro
        termo_pesquisa = self.request.GET.get('query')
        if termo_pesquisa != '':
            object_list = self.model.objects.filter(id_sensor__contains = termo_pesquisa)
            return object_list
        
        else:
            return None