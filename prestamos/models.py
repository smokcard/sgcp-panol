from django.db import models
from django.utils import timezone
from authentication.models import Trabajador, Panolero
from inventario.models import Herramienta

class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='prestamos')
    panolero = models.ForeignKey(Panolero, on_delete=models.SET_NULL, null=True, blank=True, related_name='prestamos_atendidos')
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_limite_devolucion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Préstamo #{self.id_prestamo} - {self.trabajador.usuario.nombre}"

class DetallePrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='detalles')
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name='prestamos_detalle')
    devuelto = models.BooleanField(default=False)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    observacion_entrega = models.CharField(max_length=255, blank=True, default='')
    observacion_devolucion = models.CharField(max_length=255, blank=True, default='Recepción Conforme')

    def __str__(self):
        return f"Detalle #{self.id}: {self.herramienta.codigo_barra} (Devuelto: {self.devuelto})"
