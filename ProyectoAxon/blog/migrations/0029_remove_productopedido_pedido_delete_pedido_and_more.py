# Generated by Django 4.2.14 on 2025-01-03 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0028_rename_sku_productopedido_codigo_comercial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productopedido',
            name='pedido',
        ),
        migrations.DeleteModel(
            name='Pedido',
        ),
        migrations.DeleteModel(
            name='ProductoPedido',
        ),
    ]
