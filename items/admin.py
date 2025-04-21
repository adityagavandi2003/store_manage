from django.contrib import admin
from items.models import Product, Customer, Order,OrderItem

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price','purchase_price', 'stock', 'rack', 'listed_by','created_at')
    search_fields = ('name','id','listed_by')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number','created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'shop','customer', 'total_amount', 'is_paid','order_at','payment_mode')
    list_filter = ('is_paid','payment_mode')
    search_fields = ('shop__username','razorpay_order_id','customer')
    readonly_fields = ('razorpay_order_id','razorpay_payment_id','razorpay_signature')

@admin.register(OrderItem)
class OrderItem(admin.ModelAdmin):
    list_display = ('order','product_name','product_price','quantity','subtotal')
    search_fields = ('product_name','order__order_id')