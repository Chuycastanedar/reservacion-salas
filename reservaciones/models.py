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

    # Reglas de dominio: (campo del error, validador, argumentos).
    REGLAS = (
        ('fecha', validar_fecha_no_pasada, ('fecha',)),
        ('hora_fin', validar_orden_horas, ('hora_inicio', 'hora_fin')),
        ('asistentes', validar_capacidad, ('sala', 'asistentes')),
    )

    def clean(self):
        errores = {}
        for campo, validador, nombres in self.REGLAS:
            argumentos = [self._valor_de(nombre) for nombre in nombres]
            if None in argumentos:
                continue
            try:
                validador(*argumentos)
            except ValidationError as error:
                errores.setdefault(campo, []).append(error)
        if errores:
            raise ValidationError(errores)

    def _valor_de(self, nombre):
        campo = self._meta.get_field(nombre)
        if getattr(self, campo.attname) is None:
            return None
        return getattr(self, nombre)
