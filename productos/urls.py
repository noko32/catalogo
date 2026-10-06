from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExternaAPIView, ProductoViewSet

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")

urlpatterns = [
    path("", include(router.urls)),
    path("externa/", ExternaAPIView.as_view(), name="api-externa"),
]
