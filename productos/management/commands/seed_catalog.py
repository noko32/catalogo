from decimal import Decimal
from django.core.management.base import BaseCommand
from productos.models import Producto

PRODUCTOS_POS = [
    {
        "nombre": "Terminal Punto de Venta Touch 15.6\"",
        "descripcion": "Pantalla capacitiva HD, 8GB RAM, 128GB SSD, Windows 10 IoT",
        "precio": Decimal("12499.00"),
        "stock": 5,
        "activo": True,
    },
    {
        "nombre": "Impresora Térmica de Recibos 80mm",
        "descripcion": "Corte automático, conexión USB/Ethernet, 250 mm/s",
        "precio": Decimal("2150.00"),
        "stock": 14,
        "activo": True,
    },
    {
        "nombre": "Lector de Código de Barras 2D / QR",
        "descripcion": "Sensor omnidireccional con base y gatillo manual",
        "precio": Decimal("850.50"),
        "stock": 20,
        "activo": True,
    },
    {
        "nombre": "Cajón de Dinero Metálico Automático",
        "descripcion": "5 divisiones para billetes y 8 para monedas, apertura RJ11",
        "precio": Decimal("1320.00"),
        "stock": 8,
        "activo": True,
    },
    {
        "nombre": "Báscula Digital POS 30kg",
        "descripcion": "Conexión serial RS232, plato de acero inoxidable",
        "precio": Decimal("3890.00"),
        "stock": 3,
        "activo": True,
    },
    {
        "nombre": "Rollo de Papel Térmico 80x70mm (Caja 50 pzs)",
        "descripcion": "Libre de BPA, alta sensibilidad para tickets",
        "precio": Decimal("620.00"),
        "stock": 0,  # Activo pero agotado (para probar filtro de disponibles)
        "activo": True,
    },
    {
        "nombre": "Lector de Banda Magnética USB",
        "descripcion": "Modelo descontinuado reemplazado por terminal bancaria",
        "precio": Decimal("450.00"),
        "stock": 6,  # Con stock pero inactivo (para probar filtro de disponibles)
        "activo": False,
    },
]


class Command(BaseCommand):
    help = "Puebla la base de datos con productos de ejemplo para Punto de Venta (POS)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina los productos existentes antes de sembrar los datos.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            eliminados, _ = Producto.objects.all().delete()
            self.stdout.write(f"Se eliminaron {eliminados} productos anteriores.")

        creados = 0
        actualizados = 0

        for data in PRODUCTOS_POS:
            _, created = Producto.objects.update_or_create(
                nombre=data["nombre"],
                defaults=data,
            )
            if created:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Catálogo inicializado con éxito: {creados} creados, {actualizados} actualizados."
            )
        )
