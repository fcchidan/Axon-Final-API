# Generated by Django 4.2.14 on 2025-01-02 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0025_compra_sku'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compra',
            name='usuario',
        ),
        migrations.DeleteModel(
            name='Comentario',
        ),
        migrations.DeleteModel(
            name='Compra',
        ),
    ]
