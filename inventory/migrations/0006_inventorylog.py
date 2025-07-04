# Generated by Django 5.2.1 on 2025-06-01 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adjustment_type', models.CharField(choices=[('stock-in', 'Stock In'), ('stock-out', 'Stock Out'), ('order', 'Order Fulfillment')], max_length=20)),
                ('amount', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
        ),
    ]
