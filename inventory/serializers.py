from rest_framework import serializers
from .models import Product, Supplier, Stock, Order, InventoryLog

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class InventoryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLog
        fields = '__all__'


class StockAdjustmentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True, help_text="Amount to adjust stock by. Positive for stock in, negative for stock out.")

    