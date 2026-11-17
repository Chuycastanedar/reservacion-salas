from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReservacionForm
from .models import Reservacion
from . import services
from .services import crear_reservacion


@login_required
def lista_reservaciones(request):
    reservaciones = (
        request.user.reservaciones
        .select_related('sala')
        .order_by('fecha', 'hora_inicio')
    )
    return render(
        request,
        'reservaciones/lista_reservaciones.html',
        {'reservaciones': reservaciones},
    )


@login_required
def nueva_reservacion(request):
    if request.method == 'POST':
        form = ReservacionForm(request.POST)
        if form.is_valid():
            try:
                crear_reservacion(usuario=request.user, **form.cleaned_data)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(
                    request, 'La reservación se registró correctamente.')
                return redirect('lista_reservaciones')
    else:
        form = ReservacionForm()
    return render(
        request, 'reservaciones/reservacion_form.html', {'form': form})


@login_required
def cancelar_reservacion(request, pk):
    reservacion = get_object_or_404(Reservacion, pk=pk)
    if request.method == 'POST':
        services.cancelar_reservacion(reservacion, request.user)
        return redirect('lista_reservaciones')
    return render(
        request,
        'reservaciones/confirmar_cancelacion.html',
        {'reservacion': reservacion},
    )
