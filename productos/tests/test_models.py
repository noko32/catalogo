from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase

from productos.models import Producto


class ProductoModelTests(TestCase):
    def test_creacion_producto_valido(self):
        producto = Producto.objects.create(
            nombre="Teclado Mecánico",
            descripcion="Switches cherry red",
            precio=Decimal("89.99"),
            stock=15,
            activo=True,
        )
        self.assertEqual(producto.nombre, "Teclado Mecánico")
        self.assertEqual(str(producto), "Teclado Mecánico ($89.99)")
        self.assertTrue(producto.activo)

    def test_validacion_precio_negativo_o_cero(self):
        producto = Producto(
            nombre="Mousepad",
            precio=Decimal("0.00"),
            stock=5,
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()

    def test_validacion_stock_negativo(self):
        producto = Producto(
            nombre="Monitor",
            precio=Decimal("199.99"),
            stock=-1,
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()
