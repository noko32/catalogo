from decimal import Decimal
from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "activo",
            "fecha_creacion",
        ]
        read_only_fields = ["id", "fecha_creacion"]

    def validate_nombre(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return cleaned

    def validate_precio(self, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    def validate_stock(self, value: int) -> int:
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value
