from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'stock', StockViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'logs', InventoryLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

