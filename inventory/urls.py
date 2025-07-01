from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    SupplierViewSet,
    StockViewSet,
    OrderViewSet,
    InventoryLogViewSet,
    CartViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'stock', StockViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'logs', InventoryLogViewSet)
router.register(r'carts', CartViewSet, basename='cart')


urlpatterns = [
    path('', include(router.urls)),
]

