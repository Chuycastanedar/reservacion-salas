from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .validators import (
    validar_capacidad, validar_fecha_no_pasada, validar_orden_horas)


class Sala(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    capacidad = models.PositiveIntegerField()
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Reservacion(models.Model):
    class Estado(models.TextChoices):
        VIGENTE = 'VIGENTE', 'Vigente'
        CANCELADA = 'CANCELADA', 'Cancelada'

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
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.VIGENTE,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f'{self.sala} · {self.fecha:%Y-%m-%d} '
            f'{self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M} '
            f'({self.estado})'
        )

    def clean(self):
        if self.fecha is not None:
            try:
                validar_fecha_no_pasada(self.fecha)
            except ValidationError as error:
                raise ValidationError({'fecha': error})
        if self.hora_inicio is not None and self.hora_fin is not None:
            try:
                validar_orden_horas(self.hora_inicio, self.hora_fin)
            except ValidationError as error:
                raise ValidationError({'hora_fin': error})
        if self.sala_id is not None and self.asistentes is not None:
            try:
                validar_capacidad(self.sala, self.asistentes)
            except ValidationError as error:
                raise ValidationError({'asistentes': error})
