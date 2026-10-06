# Catálogo de Productos — API REST

Prueba técnica en Python / Django para FIIXCOM Soluciones.
Implementa una API REST para la gestión de un catálogo de productos con Django REST Framework, consumo de un servicio externo con manejo de errores y una función utilitaria en Python puro.

---

## Requisitos

- Python 3.10+ (probado y validado en Python 3.12)
- SQLite3

---

## Instalación y ejecución

```bash
# 1. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones
python manage.py migrate

# 4. Poblar catálogo con datos de prueba (Punto de Venta)
python manage.py seed_catalog

# 5. Iniciar servidor
python manage.py runserver
```

La API estará disponible en `http://127.0.0.1:8000/api/` y el panel de administración en `http://127.0.0.1:8000/admin/`.

---

## Pruebas automatizadas

La suite incluye 25 pruebas automatizadas que cubren CRUD, validaciones, consultas al ORM, simulación de respuestas de red mediante mocks, comando de seed y la función utilitaria:

```bash
# Ejecutar todas las pruebas
python manage.py test

# Con detalle por prueba
python manage.py test -v 2
```

---

## Endpoints

Ruta base: `http://127.0.0.1:8000/api/`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/productos/` | Lista todos los productos |
| `POST` | `/api/productos/` | Crea un producto |
| `GET` | `/api/productos/<id>/` | Detalle de un producto |
| `PUT` | `/api/productos/<id>/` | Actualización completa |
| `PATCH` | `/api/productos/<id>/` | Actualización parcial |
| `DELETE` | `/api/productos/<id>/` | Elimina un producto |
| `GET` | `/api/productos/disponibles/` | Filtra productos con `activo=True` y `stock > 0` |
| `GET` | `/api/externa/` | Consulta API pública (JSONPlaceholder) con timeout y retorna campos seleccionados (`id`, `titulo`, `completado`) |

### Ejemplos con `curl`

**Crear producto:**
```bash
curl -X POST http://127.0.0.1:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Teclado Mecánico",
    "descripcion": "Switches táctiles",
    "precio": "89.99",
    "stock": 10,
    "activo": true
  }'
```

**Consultar productos disponibles:**
```bash
curl http://127.0.0.1:8000/api/productos/disponibles/
```

**Consultar API externa:**
```bash
curl http://127.0.0.1:8000/api/externa/
```

---

## Función utilitaria (Python puro)

Ubicada en `productos/utils.py`. Filtra diccionarios con stock mayor a cero y los ordena por precio ascendente, sin dependencias del ORM ni de Django:

```python
from productos.utils import filtrar_y_ordenar_productos

items = [
    {"nombre": "A", "precio": 100, "stock": 0},
    {"nombre": "B", "precio": 50, "stock": 4},
    {"nombre": "C", "precio": 80, "stock": 2},
]

resultado = filtrar_y_ordenar_productos(items)
# [{'nombre': 'B', 'precio': 50, 'stock': 4}, {'nombre': 'C', 'precio': 80, 'stock': 2}]
```

---

## Decisiones técnicas

- **ModelViewSet vs Generic Views:** Utilicé `ModelViewSet` con `DefaultRouter` porque mantiene la configuración de rutas REST en un solo lugar y permite registrar endpoints adicionales de colección (como `/api/productos/disponibles/`) con el decorador `@action(detail=False)`, sin tener que fragmentar el recurso en múltiples vistas genéricas (`ListCreateAPIView` y `RetrieveUpdateDestroyAPIView`).
- **Filtrado en base de datos e índice compuesto:** En `/api/productos/disponibles/`, el filtro (`activo=True, stock__gt=0`) se delega directamente a SQL a través del ORM, evitando cargar registros innecesarios en memoria en Python. Se configuró además un índice compuesto `idx_prod_activo_stock` sobre `(activo, stock)` para optimizar esta consulta recurrente.
- **Invariantes en base de datos:** Además de las validaciones en el serializador de DRF, se definieron `CheckConstraint` a nivel modelo (`precio > 0` y `stock >= 0`), protegiendo la integridad de los datos directamente en el motor de base de datos.
- **Manejo de errores en API externa:** En `/api/externa/` se definió un timeout explícito de 5 segundos y se capturan excepciones de red (`Timeout` y `ConnectionError`) devolviendo códigos de estado 504 y 502, previniendo que una falla del servicio externo cuelgue el proceso o devuelva un 500 no controlado.
- **Mocks en pruebas:** En las pruebas de la API externa se empleó `unittest.mock.patch` para simular las respuestas HTTP, garantizando que la suite se ejecute de forma rápida, determinista y sin requerir conexión a internet.
