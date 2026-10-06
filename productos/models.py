from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default="")
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=["activo", "stock"], name="idx_prod_activo_stock"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gt=0),
                name="check_producto_precio_gt_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name="check_producto_stock_gte_zero",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} (${self.precio})"
