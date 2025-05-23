# Generated by Django 5.2 on 2025-05-08 14:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('items', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyFinanceSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('total_sales', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('other_income', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('profit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('profit_margin', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FinanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('income', 'Income'), ('expense', 'Expense')], max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('description', models.TextField(blank=True, max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shop_name', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MonthlyFinanceSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('total_sales', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('other_income', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('total_expenses', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('profit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('profit_margin', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('recorded_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('top_products', models.ManyToManyField(blank=True, to='items.orderitem')),
            ],
            options={
                'unique_together': {('shop', 'month', 'year')},
            },
        ),
    ]
