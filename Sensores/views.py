from django.views.generic import ListView, DetailView
from .models import Sensor
import csv, json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import matplotlib.pyplot as plt
import io, base64
from .validators import valida_json, valida_arquivo, valida_equipmentId, valida_timestamp, valida_value

# Create your views here.

@csrf_exempt
def dados_json(request):

    if request.method != 'POST':
        return JsonResponse({"erro": 'API só recebe requisições do tipo POST'})

    dados_sensor = json.loads(request.body)
    
    try:
        equipmentId, timestamp, value = valida_json(dados_sensor)
    
    except Exception as erro:
        msg = 'Json nao foi inserido. '
        msg += str(erro)
        return JsonResponse({"erros": msg})
    
    try:
        valida_equipmentId(equipmentId)  
        timestamp_recebido = timestamp
        timestamp = valida_timestamp(timestamp_recebido)
        value = valida_value(value)
        
    except Exception as erro:
        msg = str("Json nao foi inserido.")
        erro = str(erro)
        msg += erro
        return JsonResponse({"erros": msg})


    #verifica se sensor ja existe no BD
    if Sensor.sensor_existe(equipmentId) == False:

        #Construtor padrão do Django. Instancia novo objeto da classe Sensor e salva no BD.
        name = 'testex'+ equipmentId 
        sensor = Sensor.objects.create(id_sensor = equipmentId, nome = name )
            
    sensor = Sensor.objects.get(id_sensor = equipmentId)

    try:
        sensor.criar_Leitura(timestamp, value) 
    
    except:
        return JsonResponse({"codigo": 400, "erro": f"Json NAO foi inserido. Ja existe uma leitura associada a:{equipmentId, timestamp_recebido}. Um mesmo sensor NAO pode ter mais de uma leitura em um mesmo instante de tempo."})
            
    return JsonResponse({"codigo":201, "mensagem":"Json recebido com sucesso"})





@csrf_exempt
def dados_csv(request):

    if request.method != 'POST':
        return JsonResponse({"erros": 'API só recebe requisições do tipo POST'})
    
    erros = []  
    
    try:
        arquivo = valida_arquivo(request.body)
    
    except Exception as erro:
        erro = str(erro)
        erros.append(erro)
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
            
        
        equipmentId, timestamp, value = linha[0].split(';')
        
        try:
            valida_equipmentId(equipmentId)  
            timestamp_recebido = timestamp
            timestamp = valida_timestamp(timestamp)
            value = valida_value(value)
        
        except Exception as erro:
            msg = f"A linha:{str(linha)} NAO foi inserida. "
            msg += str(erro)
            erros.append(msg)
            continue

        if Sensor.sensor_existe(equipmentId) == False:
            name = 'testex'+ equipmentId
            sensor = Sensor.objects.create(id_sensor = equipmentId, nome = name)
        
        else:
            sensor = Sensor.objects.get(id_sensor = equipmentId)
        
        try:
            sensor.criar_Leitura(timestamp, value)
        
        except:
            erros.append({"codigo": 400, "mensagem": f"A linha:{str(linha)} NAO foi inserida. Pois ja existe uma leitura associada a:{equipmentId, timestamp_recebido}. Um mesmo sensor NAO pode ter mais de uma leitura em um mesmo instante de tempo."})

    
    mensagem = 'recebi o arquivo csv com sucesso'
    
    if len(erros) > 0:
        return JsonResponse({"mensagem": mensagem, "erros": erros})
    
    else:
        return JsonResponse({"codigo":201, "mensagem": mensagem})        


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