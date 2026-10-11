import io
import qrcode
import barcode
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

class EstadoHerramienta(models.TextChoices):
    DISPONIBLE = 'DISPONIBLE', _('Disponible')
    PRESTADA = 'PRESTADA', _('Prestada')
    EN_MANTENCION = 'EN_MANTENCION', _('En Mantención')
    DE_BAJA = 'DE_BAJA', _('De Baja')

class Herramienta(models.Model):
    codigo_barra = models.CharField(max_length=50, unique=True, db_index=True, blank=True)
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=20,
        choices=EstadoHerramienta.choices,
        default=EstadoHerramienta.DISPONIBLE,
        db_index=True
    )
    foto = models.ImageField(upload_to='herramientas/', null=True, blank=True)
    codigo_qr = models.ImageField(upload_to='qrcodes/', null=True, blank=True)
    imagen_barra = models.ImageField(upload_to='barcodes/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. Generar código correlativo si no se especifica
        if not self.codigo_barra:
            ultimo = Herramienta.objects.all().order_by('-id').first()
            siguiente_id = (ultimo.id + 1) if ultimo else 1
            self.codigo_barra = f"HER-{siguiente_id:05d}"

        # 2. Generar imagen de Código de Barras (Code128)
        if not self.imagen_barra and self.codigo_barra:
            buffer_bar = BytesIO()
            code128 = Code128(self.codigo_barra, writer=ImageWriter())
            code128.write(buffer_bar, options={'write_text': True, 'font_size': 10, 'text_distance': 4})
            self.imagen_barra.save(f"bar_{self.codigo_barra}.png", ContentFile(buffer_bar.getvalue()), save=False)

        # 3. Generar imagen de Código QR
        if not self.codigo_qr and self.codigo_barra:
            qr = qrcode.QRCode(version=1, box_size=8, border=2)
            qr.add_data(self.codigo_barra)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            buffer_qr = BytesIO()
            img_qr.save(buffer_qr, format='PNG')
            self.codigo_qr.save(f"qr_{self.codigo_barra}.png", ContentFile(buffer_qr.getvalue()), save=False)

        super().save(*args, **kwargs)

    def esta_disponible(self) -> bool:
        return self.estado == EstadoHerramienta.DISPONIBLE

    def __str__(self):
        return f"[{self.codigo_barra}] {self.nombre} - {self.estado}"
