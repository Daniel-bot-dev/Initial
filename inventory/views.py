from rest_framework import viewsets, permissions
from .models import Product, Supplier, Stock, Order, InventoryLog
from .serializers import (
    ProductSerializer, SupplierSerializer, StockSerializer,
    OrderSerializer, InventoryLogSerializer, StockAdjustmentSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db.models import F
from rest_framework.permissions import IsAdminUser
from rest_framework import serializers
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_products = Product.objects.filter(stock__quantity__lt=F('min_stock'))
        serializer = self.get_serializer(low_stock_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stock_report(self, request):

        products = Product.objects.all()
        data = []
        for product in products:
            stock = getattr(product, 'stock', None)
            data.append({
                "product": product.name,
                "sku": product.sku,
                "current_stock": stock.quantity if stock else 0,
                "min_stock": product.min_stock,
            })
        return Response(data)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    @swagger_auto_schema(method='post', request_body=StockAdjustmentSerializer)
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def adjust(self, request, pk=None):
        stock = self.get_object()
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        if stock.quantity + amount < 0:
            return Response({"error": "Stock cannot go below zero."}, status=400)
        stock.quantity += amount
        stock.save()
        InventoryLog.objects.create(
            product=stock.product,
            adjustment_type='stock-in' if amount > 0 else 'stock-out',
            amount=amount
        )
        return Response({"message": "Stock adjusted.", "new_quantity": stock.quantity}, status=200)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        stock = Stock.objects.get(product=product)
        if stock.quantity < quantity:
            raise serializers.ValidationError("Not enough stock to fulfill this order.")
        order = serializer.save()
        stock.quantity -= quantity
        stock.save()
        InventoryLog.objects.create(
            product=order.product,
            adjustment_type='order',
            amount=-order.quantity
        )

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdminUser()]
        return super().get_permissions()

class InventoryLogViewSet(viewsets.ModelViewSet):
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user, checked_out=False)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        # Check if item already in cart
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity
        item.save()
        return Response({'status': 'item added', 'item': CartItemSerializer(item).data})