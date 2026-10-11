from django.urls import path
from .views import despacho_home_view, PrestamoController

urlpatterns = [
    path('', despacho_home_view, name='meson_despacho'),
    path('', despacho_home_view, name='despacho_home'),
    path('api/registrar/', PrestamoController.as_view(), name='api_registrar_prestamo'),
]
