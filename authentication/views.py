from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Usuario, Panolero

def root_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if getattr(request.user, 'es_administrador', False):
        return redirect('gestion_inventario')
    return redirect('despacho_home')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('root')

    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        password = request.POST.get('password', '')
        usuario = authenticate(username=rut, password=password)

        if usuario:
            if not usuario.is_active:
                messages.error(request, "Usuario bloqueado o inhabilitado.")
            else:
                login(request, usuario)
                if usuario.es_administrador:
                    return redirect('gestion_inventario')
                return redirect('despacho_home')
        else:
            messages.error(request, "RUT o contraseña incorrectos.")

    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def registro_view(request):
    if request.method == 'POST':
        rut = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        rol = request.POST.get('rol', 'PANOLERO')
        turno = request.POST.get('turno', '').strip()

        if not rut or not nombre or not email or not password:
            messages.error(request, "Todos los campos obligatorios deben completarse.")
            return render(request, 'auth/registro.html')

        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, f"El RUT {rut} ya se encuentra registrado.")
            return render(request, 'auth/registro.html')

        es_admin = (rol == 'ADMINISTRADOR')
        user = Usuario.objects.create_user(
            rut=rut,
            nombre=nombre,
            email=email,
            password=password,
            es_administrador=es_admin,
            is_staff=es_admin
        )

        if not es_admin:
            Panolero.objects.create(usuario=user, turno=turno or "General")

        messages.success(request, f"Cuenta de {rol} creada exitosamente. Inicia sesión.")
        return redirect('login')

    return render(request, 'auth/registro.html')
