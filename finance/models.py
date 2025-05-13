from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from decimal import Decimal
import calendar
from items.models import OrderItem
# Create your models here.

class FinanceRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('income','Income'),
        ('expense','Expense')
    ]

    shop = models.ForeignKey(User, related_name='shop_name', on_delete=models.CASCADE)
    category = models.CharField(choices=RECORD_TYPE_CHOICES,max_length=50)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(max_length=255,blank=True)
    create_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.category} - {self.amount} on {self.create_at}'

    @property
    def is_income(self):
        return self.category and self.category == 'income'

    @property
    def is_expense(self):
        return self.category and self.category == 'expense'
    
class DailyFinanceSummary(models.Model):
    shop = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField(null=True,blank=True)

    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Only product sales
    other_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # Extra sources
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # total_sales  - expenses
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # auto-calculate

    recorded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['shop', 'recorded_at'], name='unique_shop_recorded_at')
            ]

    @property
    def roi(self):
        if self.total_expenses > 0:
            roi_percent = ((self.profit) / self.total_expenses) * Decimal('100.00')
            return round(roi_percent, 2)
        return Decimal('0.00')

    
    @property
    def net_balance(self):
        return self.profit + self.other_income

    def calculate_profit(self):
        # Ensure total_sales and total_expenses are valid decimals
        total_sales = self.total_sales if self.total_sales else Decimal('0.00')
        total_expenses = self.total_expenses if self.total_expenses else Decimal('0.00')
        
        # Calculate profit and profit_margin safely
        self.profit = total_sales - total_expenses
        self.profit_margin = (
            (self.profit / total_sales * Decimal('100.00')) if total_sales > 0 else Decimal('0.00')
        )
        self.save()

    def __str__(self):
        return f"{self.shop.username} - {self.recorded_at} Summary"

class MonthlyFinanceSummary(models.Model):
    shop = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(null=True,blank=True)
    year = models.PositiveSmallIntegerField(null=True,blank=True)

    total_sales = models.DecimalField(max_digits=15, decimal_places=2, default=0)   # Only product sales
    other_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)   # Income other than sales
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # total_sales - expenses

    profit_margin = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    top_products = models.ManyToManyField(OrderItem, blank=True)

    recorded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.shop.username} - {self.month}/{self.year} Summary"

    @property
    def roi(self):
        if self.total_expenses > 0:
            roi_percent = ((self.profit) / self.total_expenses) * 100
            return round(roi_percent, 2)
        return Decimal('0.00')

    @property
    def month_name(self):
        return calendar.month_name[self.month]

    @property
    def net_balance(self):
        # Calculate net_balance dynamically
        return self.profit + self.other_income

    def calculate_profit(self):
        total_sales = self.total_sales if self.total_sales else Decimal('0.00')
        total_expenses = self.total_expenses if self.total_expenses else Decimal('0.00')

        self.profit = total_sales - total_expenses
        self.profit_margin = (
            (self.profit / total_sales * Decimal('100.00')) if total_sales > 0 else Decimal('0.00')
        )
        self.save()
