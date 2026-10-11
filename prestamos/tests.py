from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import Usuario, Trabajador, Panolero
from inventario.models import Herramienta, EstadoHerramienta
from prestamos.models import Prestamo

class PrestamoTestingSuite(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.u_pan = Usuario.objects.create_user(rut="11.111.111-1", nombre="Pañolero", email="p@p.cl", password="Password2026!")
        Panolero.objects.create(usuario=self.u_pan, turno="Mañana")
        self.client.force_authenticate(user=self.u_pan)

        self.u_trab = Usuario.objects.create_user(rut="18.452.731-6", nombre="Carlos", email="c@c.cl")
        self.trabajador = Trabajador.objects.create(usuario=self.u_trab, cargo="Técnico", area_trabajo="Mecánica")

        self.h_disp = Herramienta.objects.create(codigo_barra="HER-001", nombre="Taladro", categoria="Eléctrica")
        self.h_mant = Herramienta.objects.create(codigo_barra="HER-002", nombre="Esmeril", categoria="Eléctrica", estado=EstadoHerramienta.EN_MANTENCION)

    def test_cp_pres_01_prestamo_exitoso(self):
        resp = self.client.post("/prestamos/api/registrar/", {"rut": "18.452.731-6", "codigos": ["HER-001"]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.h_disp.refresh_from_db()
        self.assertEqual(self.h_disp.estado, EstadoHerramienta.PRESTADA)

    def test_cp_pres_02_herramienta_no_disponible(self):
        resp = self.client.post("/prestamos/api/registrar/", {"rut": "18.452.731-6", "codigos": ["HER-002"]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cp_pres_03_trabajador_bloqueado(self):
        self.trabajador.bloqueado = True
        self.trabajador.save()
        resp = self.client.post("/prestamos/api/registrar/", {"rut": "18.452.731-6", "codigos": ["HER-001"]}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
