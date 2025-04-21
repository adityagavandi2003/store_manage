from django.contrib import admin
from finance.models import FinanceRecord,MonthlyFinanceSummary,DailyFinanceSummary

# Register your models here.

@admin.register(FinanceRecord)
class FinanceRecordAdmin(admin.ModelAdmin):
    list_display = ('shop','category','amount','description','create_at')


@admin.register(DailyFinanceSummary)
class DailyFinanceAdmin(admin.ModelAdmin):
    list_display = ('shop','day','total_sales','total_expenses','other_income','profit','profit_margin','recorded_at')

    # Automatically calculate profit before saving
    def save_model(self, request, obj, form, change):
        obj.calculate_profit() 
        super().save_model(request, obj, form, change)

@admin.register(MonthlyFinanceSummary)
class MonthlyFinanceAdmin(admin.ModelAdmin):
    list_display = ('shop','month','year','total_sales','total_expenses','other_income','profit','profit_margin','recorded_at')

    # Automatically calculate profit before saving
    def save_model(self, request, obj, form, change):
        obj.calculate_profit() 
        super().save_model(request, obj, form, change)