from django import forms

from .models import Reservacion, Sala


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
        error_messages = {
            'sala': {
                'invalid_choice':
                    'La sala no se encuentra disponible para reservación.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sala'].queryset = Sala.objects.filter(activa=True)
