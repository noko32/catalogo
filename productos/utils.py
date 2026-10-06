from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List


def _parsear_precio(valor: Any) -> Decimal:
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


def _tiene_stock(valor: Any) -> bool:
    try:
        return int(valor) > 0
    except (TypeError, ValueError):
        return False


def filtrar_y_ordenar_productos(
    productos: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Filtra productos con stock > 0 y los ordena por precio ascendente.
    """
    if not isinstance(productos, list):
        raise TypeError("El argumento 'productos' debe ser una lista.")

    productos_con_stock = [
        dict(item)
        for item in productos
        if isinstance(item, dict) and _tiene_stock(item.get("stock"))
    ]

    return sorted(
        productos_con_stock,
        key=lambda item: _parsear_precio(item.get("precio")),
    )
