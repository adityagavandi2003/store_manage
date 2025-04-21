from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from datetime import datetime,date,timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from finance.models import MonthlyFinanceSummary,DailyFinanceSummary
from django.db.models.functions import TruncWeek
from items.models import Order
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from collections import Counter
from django.core.paginator import Paginator
import random
from django.db.models.functions import TruncDate
# Create your views here.

# store all finance summary here to access easily
class FinanceSummary():
    """All Finance summary week,daily,month,year """
    def get_daily_finance_data(self,shop,day,year,*args, **kwargs):
        """ Helper function to get daily finance data (revenue and expenses). """
        try:
            daily_data = DailyFinanceSummary.objects.filter(shop=shop,day=day).first()
            daily_orders = Order.objects.filter(shop=shop,order_at__day=day,order_at__year=year)

            # Extract product info
            daily_products = [product for product in daily_data.top_products.all()] if daily_data else []
            product_counter = Counter()
            for product in daily_products:  
                product_counter[product.product_name] += product.quantity

            # Get top 50 products
            top_products = [
                {'product': name, 'quantity': qty}
                for name, qty in product_counter.most_common(50)
            ]
            
            return [daily_data,top_products,daily_orders]
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], []]

    def get_week_finance_data(self,shop):
        """Helper function to get weekly finance data (revenue and expense)"""
        try:
            pass
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], []]

    def get_monthly_finance_data(self, shop, month, year,*args, **kwargs):
        """ Helper function to get monthly finance data (revenue and expenses). """
        try:
            month_data = MonthlyFinanceSummary.objects.filter(shop=shop,month=month,year=year).first()
            month_orders = Order.objects.filter(shop=shop,order_at__month=month,order_at__year=year)

            # Extract product info
            month_products = [product for product in month_data.top_products.all()] if month_data else []
            product_counter = Counter()
            for product in month_products:  
                product_counter[product.product_name] += product.quantity

            # Get top 50 products
            top_products = [
                {'product': name, 'quantity': qty}
                for name, qty in product_counter.most_common(50)
            ]
            return [month_data,top_products,month_orders]
        except Exception as e:
            print("Error in get_month_finance_data:", e)
            return [[], [], []]
    
    def get_year_finance_data(self, shop, year,*args, **kwargs):
        """ Helper function to get monthly finance data (revenue and expenses). """
        try:
            year_summary = MonthlyFinanceSummary.objects.filter(shop=shop,recorded_at__year=year)
            year_orders = Order.objects.filter(shop=shop,order_at__year=year)
            if year_summary:
                year_data = year_summary.aggregate(
                    profit=Sum('profit'),
                    total_expenses=Sum('total_expenses'),
                    total_sales=Sum('total_sales'),
                )
                profit = year_data.get('profit') or 0
                other_income = year_data.get('other_income') or 0
                year_data['net_balance'] = profit + other_income  
            else:
                year_data = {'total_profit': 0, 'total_expense': 0, 'total_revenue': 0}

            for i in range(0,len(year_summary)):
                # Extract product info
                year_products = [product for product in year_summary[i].top_products.all()] if year_data else []
                product_counter = Counter()
                for product in year_products:  
                    product_counter[product.product_name] += product.quantity

                # Get top 50 products
                top_products = [
                    {'product': name, 'quantity': qty}
                    for name, qty in product_counter.most_common(50)
                ]
            return [year_data,top_products,year_orders]
        except Exception as e:
            print("Error in get_year_finance_data:", e)
            return [[], [], []]

class FinanceDashboard(LoginRequiredMixin,FinanceSummary,View):
    def get(self,request,*args, **kwargs):
        month_search =  request.GET.get('fullmonth').split('-')[1] if request.GET.get('fullmonth') else None
        year_search = request.GET.get('fullmonth').split('-')[0] if request.GET.get('fullmonth') else None
        yesterday_search = request.GET.get('yesterday')
        year = datetime.now().year
        today = datetime.now().day
        shop = request.user
        # week = self.get_week_finance_data(shop=shop)
        # print(week)
        if month_search and year_search:
            data = self.get_monthly_finance_data(shop,month_search,year_search)
        elif year_search:
            data = self.get_year_finance_data(shop,year_search)
        elif yesterday_search:
            yesterday = today - 1
            data = self.get_daily_finance_data(shop,yesterday,year)
        else:
            data = self.get_daily_finance_data(shop,today,year)

        monthly_summary = MonthlyFinanceSummary.objects.filter(shop=shop).order_by('-year','-month')


        paginator = Paginator(monthly_summary, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'monthly_summary': page_obj,
            'month': data[0] if data else '',
            'top_products': data[1] if data else '', 
            'order':data[2] if data else '',
        }

        if month_search and year_search:
            context['search'] = {
                'month': month_search,
                'year': year_search
            }

        return render(request,'financedashboard.html',context)
    

class RevenueChart(View):
    def get(self, request, *args, **kwargs):
        shop = request.user
        today = date.today()
        start_date = today - timedelta(days=9)

        # Get summaries grouped by day
        data_qs = DailyFinanceSummary.objects.filter(
            shop=shop,
            recorded_at__date__range=(start_date, today)
        )
        # Prepare chart data
        labels = []
        profit_data = []
        sales_data = []
        expense_data = []

        for entry in data_qs:
            labels.append(entry.day)
            profit_data.append(entry.profit or 0)
            sales_data.append(entry.total_sales or 0)
            expense_data.append(entry.total_expenses or 0)

        data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Profit",
                    "data": profit_data,
                    "borderColor": "#1e5f3f",  # Green
                    'backgroundColor': '#2e8b57',
                    "fill": True,
                    "tension": 0.4,
                    'barThickness': 10,
                },
                {
                    "label": "Sales",
                    "data": sales_data,
                    "borderColor": "#1e90ff",  # Blue
                    'backgroundColor': '#0d5fa5',
                    "fill": True,
                    "tension": 0.4,
                    'barThickness':10,
                },
                {
                    "label": "Expenses",
                    "data": expense_data,
                    "borderColor": "#dc143c",  # Red
                    'backgroundColor': '#a10e2d', 
                    "fill": True,
                    "tension": 0.4,
                    'barThickness': 10,
                },
            ],
        }
        return JsonResponse(data)

class ProductChart(View):
    def get(self, request, *args, **kwargs):
        shop = request.user
        today = date.today()
        start_date = today - timedelta(days=30)
        # Get recent DailyFinanceSummary records
        summaries = DailyFinanceSummary.objects.filter(
            shop=shop,
            recorded_at__date__range=(start_date, today)
        )

        product_counter = Counter()
        for summary in summaries:
            for product in summary.top_products.all():
                product_counter[product.product_name] += product.quantity

        top_10 = product_counter.most_common(10)
        labels = [x[0] for x in top_10]
        quantities = [x[1] for x in top_10]

        data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Quantity Sold",
                    "data": quantities,
                    "borderColor": "#1e5f3f",
                    "backgroundColor": "#2e8b57",
                    "fill": True,
                    "tension": 0.4,
                    "barThickness": 10,
                }
            ]
        }

        return JsonResponse(data)


# import csv

# def backup_and_cleanup():
#     old_monthly = FinanceRecord.objects.filter(period='monthly', date__lt=start_of_current_month)

#     with open("monthly_backup.csv", "a", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(['shop', 'date', 'revenue', 'expense', 'roi'])
#         for record in old_monthly:
#             writer.writerow([
#                 record.shop.username,
#                 record.date,
#                 record.revenue,
#                 record.expense,
#                 record.roi
#             ])
    
#     old_monthly.delete()
