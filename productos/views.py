import requests
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Producto
from .serializers import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(detail=False, methods=["get"], url_path="disponibles")
    def disponibles(self, request):
        """Retorna productos activos con stock mayor a cero."""
        disponibles_qs = self.get_queryset().filter(activo=True, stock__gt=0)
        serializer = self.get_serializer(disponibles_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExternaAPIView(APIView):
    """Consume una API externa con timeout y manejo de errores de conexión."""
    UPSTREAM_URL = "https://jsonplaceholder.typicode.com/todos/1"
    TIMEOUT_SECONDS = 5.0

    def get(self, request):
        try:
            response = requests.get(
                self.UPSTREAM_URL,
                timeout=self.TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            resultado = {
                "id": data.get("id"),
                "titulo": data.get("title"),
                "completado": data.get("completed"),
            }
            return Response(resultado, status=status.HTTP_200_OK)
        except requests.exceptions.Timeout:
            return Response(
                {"error": "Tiempo de espera agotado al consultar el servicio externo."},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            return Response(
                {"error": "No fue posible conectar con el servicio externo."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except requests.exceptions.RequestException as exc:
            return Response(
                {"error": f"Error al consultar el servicio externo: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
