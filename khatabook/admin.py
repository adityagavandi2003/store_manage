from django.contrib import admin
from khatabook.models import KhataBook
# Register your models here.

@admin.register(KhataBook)
class KhataBookAdmin(admin.ModelAdmin):
    list_display = ('shop','order','total_khata_amount','paid_amount','remaing_amount','created_at')

