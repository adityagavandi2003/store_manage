from django.contrib import admin
from items.models import Product, Customer, Order,OrderItem

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','purchase_price', 'stock', 'rack', 'listed_by','created_at')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number','created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'shop','customer', 'total_amount', 'is_paid','order_at','payment_mode')

@admin.register(OrderItem)
class OrderItem(admin.ModelAdmin):
    list_display = ('order','product_name','product_price','quantity','subtotal')