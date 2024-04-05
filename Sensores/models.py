from django.db import models

# Create your models here.


class Sensor(models.Model):
    id_sensor = models.CharField(max_length = 8)
    nome = models.CharField(max_length = 50)

    class Meta:
        unique_together = (('id_sensor'),)

    def __str__(self):
        return self.nome


class Leitura(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete= models.CASCADE)
    timestamp = models.DateTimeField()
    valor = models.FloatField()

    class Meta:
        unique_together = (('sensor','timestamp'),)
    
    def __str__(self):
        return 'Leitura ' + str(self.timestamp)[:19] + ' - Sensor ' + self.sensor.nome