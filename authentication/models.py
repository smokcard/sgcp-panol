from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, rut, nombre, email, password=None, **extra_fields):
        if not rut or not email:
            raise ValueError('El RUT y el correo son obligatorios')
        email = self.normalize_email(email)
        user = self.model(rut=rut, nombre=nombre, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, nombre, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('es_administrador', True)
        return self.create_user(rut, nombre, email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=12, unique=True, db_index=True)
    nombre = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    es_administrador = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['nombre', 'email']

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Trabajador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    cargo = models.CharField(max_length=100)
    area_trabajo = models.CharField(max_length=100)
    bloqueado = models.BooleanField(default=False)

    def esta_habilitado(self) -> bool:
        return not self.bloqueado and self.usuario.is_active

    def __str__(self):
        return f"{self.usuario.nombre} - {self.cargo}"

class Panolero(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    turno = models.CharField(max_length=50)

    def __str__(self):
        return f"Pañolero: {self.usuario.nombre} ({self.turno})"
