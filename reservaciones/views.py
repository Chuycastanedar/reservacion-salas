from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ReservacionForm
from .services import crear_reservacion


@login_required
def lista_reservaciones(request):
    return render(request, 'reservaciones/lista_reservaciones.html')


@login_required
def nueva_reservacion(request):
    if request.method == 'POST':
        form = ReservacionForm(request.POST)
        if form.is_valid():
            crear_reservacion(usuario=request.user, **form.cleaned_data)
            messages.success(
                request, 'La reservación se registró correctamente.')
            return redirect('lista_reservaciones')
    else:
        form = ReservacionForm()
    return render(
        request, 'reservaciones/reservacion_form.html', {'form': form})
