from rest_framework import serializers

class RegistrarPrestamoInputSerializer(serializers.Serializer):
    rut = serializers.CharField(max_length=12, trim_whitespace=True)
    codigos = serializers.ListField(child=serializers.CharField(max_length=50, trim_whitespace=True), allow_empty=False)

class PrestamoResponseSerializer(serializers.Serializer):
    id_prestamo = serializers.IntegerField(source='id')
    rut_trabajador = serializers.CharField(source='trabajador.usuario.rut')
    nombre_trabajador = serializers.CharField(source='trabajador.usuario.nombre')
    fecha_prestamo = serializers.DateTimeField()
    total_herramientas = serializers.SerializerMethodField()

    def get_total_herramientas(self, obj):
        return obj.detalles.count()
