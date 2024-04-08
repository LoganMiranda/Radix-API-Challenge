from django.db import models

# Create your models here.


class Sensor(models.Model):
    id_sensor = models.CharField(max_length = 8, unique=True)
    nome = models.CharField(max_length = 50)

    def __str__(self):
        return self.nome
    
    @classmethod
    def sensor_existe(cls, equipmentId):

        return cls.objects.filter(id_sensor=equipmentId).exists()
    


    def criar_Leitura(self, timestamp, value):
        Leitura.objects.create(sensor = self, timestamp = timestamp, valor = value)
        return None



class Leitura(models.Model):
    sensor = models.ForeignKey(Sensor, related_name='leitura' ,on_delete= models.CASCADE)
    timestamp = models.DateTimeField()
    valor = models.FloatField()

    class Meta:
        unique_together = (('sensor','timestamp'),)
    
    def __str__(self):
        return 'Leitura ' + str(self.timestamp)[:19] + ' - Sensor ' + self.sensor.nome
    
    