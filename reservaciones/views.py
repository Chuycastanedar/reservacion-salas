from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import ReservacionForm


@login_required
def lista_reservaciones(request):
    return render(request, 'reservaciones/lista_reservaciones.html')


@login_required
def nueva_reservacion(request):
    form = ReservacionForm()
    return render(
        request, 'reservaciones/reservacion_form.html', {'form': form})
