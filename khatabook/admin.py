from django.contrib import admin
from khatabook.models import KhataBook
# Register your models here.

@admin.register(KhataBook)
class KhataBookAdmin(admin.ModelAdmin):
    list_display = ('shop','order','customer_name','total_khata_amount','paid_amount','remaining_amount','created_at')

