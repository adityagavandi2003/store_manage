# Generated by Django 5.2 on 2025-06-07 19:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_orderitem_created_at_alter_order_order_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsappFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20)),
                ('rating', models.IntegerField()),
                ('comments', models.TextField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='items.order')),
            ],
        ),
    ]
