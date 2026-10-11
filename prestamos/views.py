from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inventario.models import Herramienta, EstadoHerramienta
from prestamos.models import Prestamo, DetallePrestamo
from authentication.models import Trabajador, Panolero

@login_required
def despacho_home_view(request):
    if request.method == 'POST' and request.POST.get('accion_devolucion'):
        codigo = request.POST.get('codigo_devolucion', '').strip().upper()
        obs = request.POST.get('observacion_devolucion', 'Recepción Conforme')
        a_mant = request.POST.get('a_mantencion') == 'on'

        detalle = DetallePrestamo.objects.filter(herramienta__codigo_barra=codigo, devuelto=False).last()
        if detalle:
            detalle.devuelto = True
            detalle.fecha_devolucion = timezone.now()
            detalle.observacion_devolucion = obs
            detalle.save()

            herramienta = detalle.herramienta
            if a_mant:
                herramienta.estado = EstadoHerramienta.EN_MANTENCION
            else:
                herramienta.estado = EstadoHerramienta.DISPONIBLE
            herramienta.save()

            messages.success(request, f"Herramienta {codigo} devuelta con éxito el {detalle.fecha_devolucion.strftime('%d/%m/%Y a las %H:%M')}.")
        else:
            messages.error(request, f"No se encontró un préstamo activo para la herramienta {codigo}.")
        return redirect('meson_despacho')

    herramientas = Herramienta.objects.all().order_by('-id')
    detalles_activos = DetallePrestamo.objects.filter(devuelto=False).select_related('prestamo__trabajador__usuario', 'herramienta').order_by('-prestamo__fecha_prestamo')
    detalles_devueltos = DetallePrestamo.objects.filter(devuelto=True).select_related('prestamo__trabajador__usuario', 'herramienta').order_by('-fecha_devolucion')[:15]

    context = {
        'herramientas': herramientas,
        'detalles_activos': detalles_activos,
        'detalles_devueltos': detalles_devueltos,
    }
    return render(request, 'despacho.html', context)

meson_despacho = despacho_home_view


class PrestamoController(APIView):
    def post(self, request):
        rut = request.data.get('rut', '').strip()
        codigos = request.data.get('codigos', [])

        if not rut or not codigos:
            return Response({"error": "Debe enviar RUT y al menos una herramienta."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trabajador = Trabajador.objects.get(usuario__rut=rut)
        except Trabajador.DoesNotExist:
            return Response({"error": f"No se encontró un trabajador registrado con el RUT {rut}."}, status=status.HTTP_404_NOT_FOUND)

        if trabajador.bloqueado:
            return Response({"error": "El trabajador se encuentra bloqueado para retiros."}, status=status.HTTP_400_BAD_REQUEST)

        herramientas_a_prestar = []
        for cod in codigos:
            try:
                h = Herramienta.objects.get(codigo_barra=cod)
                if h.estado != EstadoHerramienta.DISPONIBLE:
                    return Response({"error": f"La herramienta {cod} no está disponible (Estado: {h.estado})."}, status=status.HTTP_400_BAD_REQUEST)
                herramientas_a_prestar.append(h)
            except Herramienta.DoesNotExist:
                return Response({"error": f"Herramienta con código {cod} no existe."}, status=status.HTTP_404_NOT_FOUND)

        panolero = None
        if request.user.is_authenticated:
            panolero = Panolero.objects.filter(usuario=request.user).first()
        if not panolero:
            panolero = Panolero.objects.first()

        prestamo = Prestamo.objects.create(
            trabajador=trabajador,
            panolero=panolero,
            fecha_limite_devolucion=None
        )

        for h in herramientas_a_prestar:
            DetallePrestamo.objects.create(prestamo=prestamo, herramienta=h)
            h.estado = EstadoHerramienta.PRESTADA
            h.save()

        return Response({
            "mensaje": "Préstamo registrado exitosamente",
            "prestamo": {
                "id_prestamo": prestamo.id_prestamo,
                "nombre_trabajador": trabajador.usuario.nombre,
                "rut": trabajador.usuario.rut
            }
        }, status=status.HTTP_201_CREATED)
