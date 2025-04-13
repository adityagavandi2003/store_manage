# import uuid

# idd = uuid.uuid4()
# # Convert UUID to string before splitting
# sp = str(idd).split('-')
# print("Split UUID:", f'#SALE00{sp[0]}')


# from django.db import models
# from django.utils import timezone

# class FinanceOverview(models.Model):
#     """
#     Represents the financial overview for a specific period (e.g., monthly).
#     While the image shows "this month," you might want to store historical data as well.
#     """
#     period_start = models.DateField(default=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
#                                     help_text="Start date of the financial period.")
#     period_end = models.DateField(help_text="End date of the financial period.")
#     profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     sales = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     net_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
#                                        help_text="Current balance overview for this period.")

#     class Meta:
#         verbose_name = "Finance Overview"
#         verbose_name_plural = "Finance Overviews"
#         ordering = ['-period_start']
#         unique_together = ('period_start', 'period_end') # To avoid duplicate entries for the same period

#     def __str__(self):
#         return f"Finance Overview for {self.period_start} to {self.period_end}"

# class Income(models.Model):
#     """
#     Represents different sources of income.
#     """
#     overview = models.ForeignKey(FinanceOverview, related_name='incomes', on_delete=models.CASCADE)
#     source = models.CharField(max_length=255)
#     amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

#     def __str__(self):
#         return f"{self.source}: ₹{self.amount}"

# class Expense(models.Model):
#     """
#     Represents different categories of expenses.
#     """
#     overview = models.ForeignKey(FinanceOverview, related_name='expenses_details', on_delete=models.CASCADE)
#     category = models.CharField(max_length=255)
#     amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

#     def __str__(self):
#         return f"{self.category}: ₹{self.amount}"

# class SalesPerformance(models.Model):
#     """
#     Represents key metrics related to sales performance for a specific period.
#     """
#     overview = models.OneToOneField(FinanceOverview, related_name='sales_performance', on_delete=models.CASCADE)
#     total_orders = models.IntegerField(default=0)
#     average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

#     class Meta:
#         verbose_name_plural = "Sales Performance"

#     def __str__(self):
#         return f"Sales Performance for {self.overview.period_start} to {self.overview.period_end}"

# class KeyMetric(models.Model):
#     """
#     Represents other important financial key metrics.
#     """
#     overview = models.OneToOneField(FinanceOverview, related_name='key_metrics', on_delete=models.CASCADE)
#     profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
#                                         help_text="Profit Margin as a percentage (e.g., 36.21).")
#     return_on_investment = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
#                                                help_text="Return on Investment (ROI) as a percentage (e.g., 12.5).")

#     class Meta:
#         verbose_name_plural = "Key Metrics"

#     def __str__(self):
#         return f"Key Metrics for {self.overview.period_start} to {self.overview.period_end}"

# class MonthlyFinancialOverview(models.Model):
#     """
#     Represents the monthly financial overview table shown at the bottom.
#     This could potentially be generated from the FinanceOverview data,
#     but having a separate model allows for direct entry or specific monthly summaries.
#     """
#     month = models.DateField(help_text="The first day of the month for this overview.")
#     sales = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     profit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
#     profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
#                                          help_text="Profit Margin as a percentage.")

#     class Meta:
#         verbose_name_plural = "Monthly Financial Overview"
#         ordering = ['-month']
#         unique_together = ('month',)

#     def __str__(self):
#         return f"Financial Overview for {self.month.strftime('%B %Y')}"



# from datetime import timedelta
# from django.utils import timezone

# today = timezone.now()
# thirty_days_ago= today-timedelta(days=30)
# print(thirty_days_ago)

