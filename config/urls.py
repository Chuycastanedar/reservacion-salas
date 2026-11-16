from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'cuentas/login/',
        auth_views.LoginView.as_view(),
        name='login',
    ),
    path(
        'cuentas/logout/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path('reservaciones/', include('reservaciones.urls')),
]
