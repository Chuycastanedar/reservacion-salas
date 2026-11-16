from django import forms

from .models import Reservacion


class ReservacionForm(forms.ModelForm):
    class Meta:
        model = Reservacion
        fields = [
            'sala',
            'fecha',
            'hora_inicio',
            'hora_fin',
            'asistentes',
            'proposito',
        ]
        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'),
            'hora_inicio': forms.TimeInput(
                attrs={'type': 'time'}, format='%H:%M'),
            'hora_fin': forms.TimeInput(
                attrs={'type': 'time'}, format='%H:%M'),
        }
