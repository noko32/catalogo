from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from productos.models import Producto


class SeedCatalogCommandTests(TestCase):
    def test_seed_catalog_crea_productos(self):
        out = StringIO()
        call_command("seed_catalog", stdout=out)

        self.assertIn("Catálogo inicializado con éxito", out.getvalue())
        self.assertGreater(Producto.objects.count(), 0)

        # Verifica que se hayan creado productos con stock y sin stock para pruebas de POS
        self.assertTrue(Producto.objects.filter(activo=True, stock__gt=0).exists())
        self.assertTrue(Producto.objects.filter(activo=True, stock=0).exists())
        self.assertTrue(Producto.objects.filter(activo=False, stock__gt=0).exists())

    def test_seed_catalog_con_clear(self):
        Producto.objects.create(
            nombre="Producto Temporal",
            precio="10.00",
            stock=1,
            activo=True,
        )
        out = StringIO()
        call_command("seed_catalog", "--clear", stdout=out)

        self.assertIn("Se eliminaron", out.getvalue())
        self.assertFalse(Producto.objects.filter(nombre="Producto Temporal").exists())
