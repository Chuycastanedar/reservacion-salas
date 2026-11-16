from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def lista_reservaciones(request):
    return render(request, 'reservaciones/lista_reservaciones.html')
