from django.test import TestCase
from .models import Sensor, Leitura        
from django.utils import timezone
import random
# Create your tests here.





class Leitura_teste(TestCase):
    def test_leitura_correta(self):
        sensor = Sensor.objects.create(id_sensor = 'EQ-12495', nome = 'teste EQ-12495' )
        #sensor = Sensor.objects.get(id_sensor = 'EQ-12495')
        for c in range(0,10):
            try:
                agora = timezone.now().astimezone(timezone.get_current_timezone())
                valor = random.uniform(0,100)
                sensor.criar_Leitura(agora, valor )
            except:
                print('erro')