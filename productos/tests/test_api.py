from decimal import Decimal
from unittest.mock import Mock, patch
from django.urls import reverse
import requests
from rest_framework import status
from rest_framework.test import APITestCase

from productos.models import Producto


class ProductoAPITests(APITestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Laptop Gamer",
            descripcion="16GB RAM, 512GB SSD",
            precio=Decimal("1200.50"),
            stock=10,
            activo=True,
        )
        self.list_url = reverse("producto-list")
        self.detail_url = reverse("producto-detail", args=[self.producto.id])
        self.disponibles_url = reverse("producto-disponibles")
        self.externa_url = reverse("api-externa")

    # --- CRUD Tests ---

    def test_crear_producto_exitoso(self):
        payload = {
            "nombre": "Mouse Inalámbrico",
            "descripcion": "Sensor óptico 1600 DPI",
            "precio": "25.00",
            "stock": 50,
            "activo": True,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Mouse Inalámbrico")
        self.assertEqual(response.data["stock"], 50)
        self.assertTrue(Producto.objects.filter(nombre="Mouse Inalámbrico").exists())

    def test_listar_productos(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_obtener_detalle_producto(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Laptop Gamer")

    def test_actualizar_producto_put(self):
        payload = {
            "nombre": "Laptop Gamer Pro",
            "descripcion": "32GB RAM, 1TB SSD",
            "precio": "1500.00",
            "stock": 8,
            "activo": True,
        }
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Laptop Gamer Pro")
        self.assertEqual(self.producto.stock, 8)

    def test_actualizar_producto_patch(self):
        payload = {"stock": 12}
        response = self.client.patch(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 12)

    def test_eliminar_producto(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Producto.objects.filter(id=self.producto.id).exists())

    # --- Validation Tests ---

    def test_validacion_nombre_vacio_o_espacios(self):
        payload = {
            "nombre": "   ",
            "precio": "30.00",
            "stock": 5,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nombre", response.data)

    def test_validacion_precio_menor_o_igual_a_cero(self):
        payload = {
            "nombre": "Cable HDMI",
            "precio": "0.00",
            "stock": 10,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("precio", response.data)

        payload["precio"] = "-5.00"
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("precio", response.data)

    def test_validacion_stock_negativo(self):
        payload = {
            "nombre": "Adaptador USB-C",
            "precio": "15.00",
            "stock": -2,
        }
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stock", response.data)

    # --- Custom Query: Disponibles (ORM level) ---

    def test_endpoint_disponibles_filtra_por_activo_y_stock(self):
        # Inactivo con stock
        Producto.objects.create(
            nombre="Producto Descontinuado",
            precio=Decimal("40.00"),
            stock=10,
            activo=False,
        )
        # Activo sin stock
        Producto.objects.create(
            nombre="Producto Agotado",
            precio=Decimal("60.00"),
            stock=0,
            activo=True,
        )
        # Activo con stock adicional
        Producto.objects.create(
            nombre="Monitor 4K",
            precio=Decimal("350.00"),
            stock=3,
            activo=True,
        )

        with self.assertNumQueries(1):
            response = self.client.get(self.disponibles_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Esperamos solo self.producto (stock=10, activo=True) y "Monitor 4K" (stock=3, activo=True)
        self.assertEqual(len(response.data), 2)
        nombres = [item["nombre"] for item in response.data]
        self.assertIn("Laptop Gamer", nombres)
        self.assertIn("Monitor 4K", nombres)
        self.assertNotIn("Producto Descontinuado", nombres)
        self.assertNotIn("Producto Agotado", nombres)

    # --- External API Proxy ---

    @patch("productos.views.requests.get")
    def test_externa_exito(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "userId": 1,
            "id": 1,
            "title": "delectus aut autem",
            "completed": False,
        }
        mock_get.return_value = mock_response

        response = self.client.get(self.externa_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["titulo"], "delectus aut autem")
        self.assertEqual(response.data["completado"], False)
        self.assertNotIn("userId", response.data)
        mock_get.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/todos/1",
            timeout=5.0,
        )

    @patch("productos.views.requests.get")
    def test_externa_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        response = self.client.get(self.externa_url)
        self.assertEqual(response.status_code, status.HTTP_504_GATEWAY_TIMEOUT)
        self.assertIn("error", response.data)

    @patch("productos.views.requests.get")
    def test_externa_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to resolve host")

        response = self.client.get(self.externa_url)
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("error", response.data)
