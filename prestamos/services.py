from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from core.exceptions import ErrorNegocioException
from authentication.models import Trabajador, Panolero
from inventario.models import EstadoHerramienta
from inventario.repositories import IHerramientaRepository, HerramientaRepositoryImpl
from prestamos.models import Prestamo, DetallePrestamo

class PrestamoService:
    def __init__(self, herramienta_repo: IHerramientaRepository = None):
        self.herramienta_repo = herramienta_repo or HerramientaRepositoryImpl()

    def procesar_salida(self, rut_trabajador: str, codigos_herramientas: list, user) -> Prestamo:
        if not codigos_herramientas:
            raise ErrorNegocioException("Debe ingresar al menos una herramienta.")

        trabajador = Trabajador.objects.filter(usuario__rut=rut_trabajador).first()
        if not trabajador:
            raise ErrorNegocioException(f"Trabajador {rut_trabajador} no encontrado.")
        if not trabajador.esta_habilitado():
            raise ErrorNegocioException("El trabajador se encuentra bloqueado.")

        panolero = Panolero.objects.filter(usuario=user).first()
        if not panolero:
            panolero, _ = Panolero.objects.get_or_create(usuario=user, defaults={'turno': 'General'})

        with transaction.atomic():
            prestamo = Prestamo.objects.create(
                trabajador=trabajador,
                panolero=panolero,
                fecha_limite_devolucion=timezone.now() + timedelta(days=1),
                estado_prestamo='VIGENTE'
            )
            for cod in codigos_herramientas:
                h = self.herramienta_repo.buscar_por_codigo(cod)
                if not h:
                    raise ErrorNegocioException(f"Herramienta {cod} no existe.")
                if not h.esta_disponible():
                    raise ErrorNegocioException(f"Activo no disponible: {h.nombre} [{cod}] está en {h.estado}.")

                DetallePrestamo.objects.create(prestamo=prestamo, herramienta=h, observacion_entrega="Despacho conforme")
                self.herramienta_repo.actualizar_estado(h.id, EstadoHerramienta.PRESTADA)

        return prestamo

    def procesar_devolucion(self, codigo: str, observacion: str = "Recepción Conforme", a_mantencion: bool = False) -> str:
        h = self.herramienta_repo.buscar_por_codigo(codigo)
        if not h:
            raise ErrorNegocioException(f"Herramienta {codigo} no existe.")

        det = DetallePrestamo.objects.filter(herramienta=h, devuelto=False).last()
        if not det:
            raise ErrorNegocioException(f"La herramienta [{codigo}] no figura como prestada.")

        with transaction.atomic():
            det.marcar_devuelto(obs=observacion)
            nuevo_estado = EstadoHerramienta.EN_MANTENCION if a_mantencion else EstadoHerramienta.DISPONIBLE
            self.herramienta_repo.actualizar_estado(h.id, nuevo_estado)

            if not det.prestamo.detalles.filter(devuelto=False).exists():
                det.prestamo.estado_prestamo = 'DEVUELTO'
                det.prestamo.save(update_fields=['estado_prestamo'])

        return f"Herramienta [{codigo}] devuelta. Nuevo estado: {nuevo_estado}."
