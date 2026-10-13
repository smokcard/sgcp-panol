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
        email = request.POST.get('email', '').strip().lower()
        nombre = request.POST.get('nombre', '').strip()
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        
        # 1. Validar si ya existe el correo
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya se encuentra registrado.')
            return render(request, 'auth/registro.html', {'rut': rut, 'nombre': nombre})

        # 2. Validar si ya existe el RUT (si tu modelo también tiene rut unique=True)
        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, 'El RUT ingresado ya está registrado.')
            return render(request, 'auth/registro.html', {'email': email, 'nombre': nombre})

        # 3. Proceder con la creación
        es_admin = (rol == 'ADMINISTRADOR')
        user = Usuario.objects.create_user(
            rut=rut,
            nombre=nombre,
            email=email,
            password=password,
            es_administrador=es_admin,
            is_staff=es_admin
        )
        messages.success(request, 'Usuario registrado con éxito. Ahora puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'auth/registro.html')