from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Usuario, Panolero

def validar_rut_chileno(rut):
    """Valida el RUT usando el algoritmo de Módulo 11."""
    rut = rut.upper().replace("-", "").replace(".", "")
    if len(rut) < 8 or len(rut) > 9:
        return False
    cuerpo = rut[:-1]
    dv_ingresado = rut[-1]
    if not cuerpo.isdigit():
        return False
    suma = 0
    multiplo = 2
    for c in reversed(cuerpo):
        suma += int(c) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    dv_calculado = 11 - (suma % 11)
    if dv_calculado == 11:
        dv_esperado = '0'
    elif dv_calculado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_calculado)
    return dv_ingresado == dv_esperado

def root_redirect_view(request):
    """Redirige la raíz del sitio según el estado de autenticación y rol."""
    if request.user.is_authenticated:
        if getattr(request.user, 'es_administrador', False):
            return redirect('gestion_inventario')
        return redirect('meson_despacho')
    return redirect('login')

def registro_view(request):
    if request.method == 'POST':
        rut_raw = request.POST.get('rut', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        rol = request.POST.get('rol', 'PANOLERO')
        turno = request.POST.get('turno', '').strip()

        contexto_previo = {'rut': rut_raw, 'nombre': nombre, 'email': email, 'rol': rol, 'turno': turno}

        # 1. Validación de RUT (Módulo 11)
        if not validar_rut_chileno(rut_raw):
            messages.error(request, f"El RUT '{rut_raw}' no es válido. Revise el dígito verificador.")
            return render(request, 'auth/registro.html', contexto_previo)

        rut = rut_raw.upper().replace(".", "")

        # 2. Validación de Correo Real
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, f"El formato del correo '{email}' es incorrecto.")
            return render(request, 'auth/registro.html', contexto_previo)

        # 3. Validación de duplicados
        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, f"El RUT {rut} ya está registrado en el sistema.")
            return render(request, 'auth/registro.html', contexto_previo)
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, f"El correo {email} ya está en uso por otro usuario.")
            return render(request, 'auth/registro.html', contexto_previo)

        # 4. Creación del usuario
        es_admin = (rol == 'ADMINISTRADOR')
        u = Usuario.objects.create_user(rut=rut, nombre=nombre, email=email, password=password, es_administrador=es_admin)
        
        if not es_admin:
            Panolero.objects.create(usuario=u, turno=turno)
            
        messages.success(request, "Cuenta creada exitosamente. Ya puede iniciar sesión.")
        return redirect('login')

    return render(request, 'auth/registro.html')

def login_view(request):
    if request.method == 'POST':
        # Buscamos 'username' o 'rut' sin importar cómo se llame en el HTML
        rut_raw = request.POST.get('username') or request.POST.get('rut', '')
        rut = rut_raw.strip().upper().replace(".", "")
        password = request.POST.get('password', '')

        user = authenticate(request, username=rut, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.nombre}")
            if user.es_administrador:
                return redirect('gestion_inventario')
            else:
                return redirect('meson_despacho')
        else:
            messages.error(request, "Credenciales incorrectas. Verifique su RUT y contraseña.")

    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('login')
