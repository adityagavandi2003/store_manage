from django.contrib import admin
from items.models import Product, Order,OrderItem

# Register your models here.
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','display_price', 'display_remaining_stock', 'stock_quantity_with_unit','listed_by','created_at']
    search_fields = ('name','listed_by__username','product_id','price')
    
    def stock_quantity_with_unit(self, obj):
        return obj.stock_quantity_with_unit
    stock_quantity_with_unit.short_description = 'Total Stock'

    def display_remaining_stock(self, obj):
        return obj.display_remaining_stock
    display_remaining_stock.short_description = 'Remaining Stock'

    def display_price(self, obj):
        return obj.display_price
    display_price.short_description = 'Price'

# 1. Inline OrderItem in Order admin
class OrderItemInline(admin.TabularInline):  # or admin.StackedInline
    model = OrderItem
    extra = 1
    # optional: make fields readonly
    readonly_fields = ('product_name','product_price','unit', 'quantity', 'subtotal')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'shop','customer', 'total_amount', 'is_paid','order_at','payment_mode')
    list_filter = ('is_paid','payment_mode')
    search_fields = ('shop__username','razorpay_order_id','customer')
    readonly_fields = ('razorpay_order_id','razorpay_payment_id','razorpay_signature')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name','product_price','stock_quantity_with_unit','quantity','subtotal','created_at')
    list_filter = ('product_name',)
    search_fields = ['product_name']

    def stock_quantity_with_unit(self, obj):
        return obj.stock_quantity_with_unit
    stock_quantity_with_unit.short_description = 'Total Stock'