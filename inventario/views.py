from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Herramienta, EstadoHerramienta
from authentication.models import Trabajador, Usuario

@login_required
def gestion_inventario_view(request):
    if not request.user.es_administrador:
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('meson_despacho')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        # Crear Herramienta
        if accion == 'crear_herramienta':
            # Si viene vacío por alguna razón, lo generamos en backend
            codigo = request.POST.get('codigo_barra', '').strip().upper()
            if not codigo:
                ultima = Herramienta.objects.order_by('-id').first()
                if ultima and ultima.codigo_barra.startswith('HER-'):
                    try:
                        n = int(ultima.codigo_barra.split('-')[1])
                        codigo = f"HER-{str(n+1).zfill(5)}"
                    except:
                        codigo = f"HER-{str(Herramienta.objects.count()+1).zfill(5)}"
                else:
                    codigo = "HER-00001"

            nombre = request.POST.get('nombre', '').strip()
            cat = request.POST.get('categoria', 'General').strip()
            foto = request.FILES.get('imagen') or request.FILES.get('foto')

            if Herramienta.objects.filter(codigo_barra=codigo).exists():
                messages.error(request, f"El código {codigo} ya está registrado.")
            else:
                h = Herramienta(codigo_barra=codigo, nombre=nombre, categoria=cat)
                if foto:
                    if hasattr(h, 'foto'):
                        h.foto = foto
                    elif hasattr(h, 'imagen'):
                        h.imagen = foto
                h.save()
                messages.success(request, f"Herramienta {codigo} creada exitosamente.")
            return redirect('gestion_inventario')

        # Crear Trabajador
        elif accion == 'crear_trabajador':
            rut = request.POST.get('rut', '').strip()
            nombre = request.POST.get('nombre', '').strip()
            email = request.POST.get('email', '').strip()
            cargo = request.POST.get('cargo', 'Operario').strip()
            area = request.POST.get('area_trabajo', 'Faena').strip()

            if Usuario.objects.filter(rut=rut).exists():
                messages.error(request, f"El RUT {rut} ya existe.")
            else:
                u = Usuario.objects.create_user(rut=rut, nombre=nombre, email=email, password='User2026!', es_administrador=False)
                Trabajador.objects.create(usuario=u, cargo=cargo, area_trabajo=area)
                messages.success(request, f"Trabajador {nombre} ({rut}) registrado exitosamente.")
            return redirect('gestion_inventario')

    herramientas = Herramienta.objects.all().order_by('-id')
    trabajadores = Trabajador.objects.select_related('usuario').all().order_by('-usuario_id')

    # Calcular el siguiente código para mostrarlo en el frontend
    ultima_herr = herramientas.first()
    if ultima_herr and ultima_herr.codigo_barra.startswith('HER-'):
        try:
            num = int(ultima_herr.codigo_barra.split('-')[1])
            siguiente_codigo = f"HER-{str(num+1).zfill(5)}"
        except:
            siguiente_codigo = f"HER-{str(herramientas.count()+1).zfill(5)}"
    else:
        siguiente_codigo = "HER-00001"

    return render(request, 'inventario/gestion.html', {
        'herramientas': herramientas,
        'trabajadores': trabajadores,
        'siguiente_codigo': siguiente_codigo
    })

# --- ACCIONES HERRAMIENTAS ---

@login_required
def editar_herramienta(request, pk):
    if not request.user.es_administrador:
        return redirect('meson_despacho')
    herramienta = get_object_or_404(Herramienta, pk=pk)

    if request.method == 'POST':
        herramienta.nombre = request.POST.get('nombre', herramienta.nombre).strip()
        herramienta.categoria = request.POST.get('categoria', herramienta.categoria).strip()
        herramienta.estado = request.POST.get('estado', herramienta.estado)
        
        foto = request.FILES.get('imagen') or request.FILES.get('foto')
        if foto:
            if hasattr(herramienta, 'foto'):
                herramienta.foto = foto
            elif hasattr(herramienta, 'imagen'):
                herramienta.imagen = foto

        herramienta.save()
        messages.success(request, f"Herramienta {herramienta.codigo_barra} actualizada.")
    return redirect('gestion_inventario')

@login_required
def eliminar_herramienta(request, pk):
    if not request.user.es_administrador:
        return redirect('meson_despacho')
    herramienta = get_object_or_404(Herramienta, pk=pk)
    cod = herramienta.codigo_barra
    herramienta.delete()
    messages.success(request, f"Herramienta {cod} eliminada correctamente.")
    return redirect('gestion_inventario')

# --- ACCIONES TRABAJADORES ---

@login_required
def editar_trabajador(request, pk):
    if not request.user.es_administrador:
        return redirect('meson_despacho')
    trabajador = get_object_or_404(Trabajador, pk=pk)

    if request.method == 'POST':
        trabajador.usuario.nombre = request.POST.get('nombre', trabajador.usuario.nombre).strip()
        trabajador.usuario.email = request.POST.get('email', trabajador.usuario.email).strip()
        trabajador.usuario.save()

        trabajador.cargo = request.POST.get('cargo', trabajador.cargo).strip()
        trabajador.area_trabajo = request.POST.get('area_trabajo', trabajador.area_trabajo).strip()
        trabajador.bloqueado = request.POST.get('bloqueado') == 'on'
        trabajador.save()

        messages.success(request, f"Trabajador {trabajador.usuario.nombre} actualizado.")
    return redirect('gestion_inventario')

@login_required
def eliminar_trabajador(request, pk):
    if not request.user.es_administrador:
        return redirect('meson_despacho')
    trabajador = get_object_or_404(Trabajador, pk=pk)
    usuario = trabajador.usuario
    nom = usuario.nombre
    trabajador.delete()
    usuario.delete()
    messages.success(request, f"Trabajador {nom} eliminado correctamente.")
    return redirect('gestion_inventario')
