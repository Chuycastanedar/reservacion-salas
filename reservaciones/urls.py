from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_reservaciones, name='lista_reservaciones'),
]
