from django.conf import settings
from django.db import models


class Sala(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    capacidad = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)


class Reservacion(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservaciones',
    )
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name='reservaciones',
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    asistentes = models.IntegerField()
    proposito = models.CharField(max_length=200)
    estado = models.CharField(max_length=20)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
