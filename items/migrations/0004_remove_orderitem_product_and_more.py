# Generated by Django 5.2 on 2025-04-13 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0003_orderitem_product_name_orderitem_product_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='product',
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product_price',
            field=models.CharField(help_text='Sell Price', max_length=15),
        ),
    ]
