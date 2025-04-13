# Generated by Django 5.2 on 2025-04-13 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0005_orderitem_subtotal'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_mode',
            field=models.CharField(choices=[('Online', 'Online'), ('Offline', 'Offline')], default='Online', max_length=50),
            preserve_default=False,
        ),
    ]
