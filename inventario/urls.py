from django.urls import path
from .views import (
    gestion_inventario_view,
    editar_herramienta,
    eliminar_herramienta,
    editar_trabajador,
    eliminar_trabajador
)

urlpatterns = [
    path('gestion/', gestion_inventario_view, name='gestion_inventario'),
    # Herramientas (pk numérico)
    path('herramienta/<int:pk>/editar/', editar_herramienta, name='editar_herramienta'),
    path('herramienta/<int:pk>/eliminar/', eliminar_herramienta, name='eliminar_herramienta'),
    # Trabajadores (pk string / RUT)
    path('trabajador/<str:pk>/editar/', editar_trabajador, name='editar_trabajador'),
    path('trabajador/<str:pk>/eliminar/', eliminar_trabajador, name='eliminar_trabajador'),
]
