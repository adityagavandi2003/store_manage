import json
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from datetime import datetime,date,timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from finance.models import MonthlyFinanceSummary,DailyFinanceSummary
from django.db.models.functions import TruncWeek
from items.models import Order
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from collections import Counter
from finance.forms import FinanceRecordForm
from finance.models import FinanceRecord
from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate
# Create your views here.

# store all finance summary here to access easily
class FinanceSummary():
    """All Finance summary week,daily,month,year """
    def get_daily_finance_data(self,shop,day,year,*args, **kwargs):
        """ Helper function to get daily finance data (revenue and expenses). """
        try:
            day = str(day).split('-')[2] if '-' in str(day) else day

            daily_data = DailyFinanceSummary.objects.filter(shop=shop,recorded_at__day=day).first()
            daily_orders = Order.objects.filter(shop=shop,order_at__day=day,order_at__year=year)
            records = FinanceRecord.objects.filter(shop=shop,create_at__day=day) # expense and income records

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
            return [daily_data,top_products,daily_orders,records]
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], [],[]]

    def get_week_finance_data(self,shop,*args, **kwargs):
        """Helper function to get weekly finance data (revenue and expense)"""
        try:
            today = date.today()
            start_date = today - timedelta(days=7)
            # Get summaries grouped by day
            week_data = DailyFinanceSummary.objects.filter(
                shop=shop,
                recorded_at__date__range=(start_date, today)
            )
            week_orders = Order.objects.filter(shop=shop,order_at__date__range=(start_date, today))
            records = FinanceRecord.objects.filter(shop=shop,create_at__date__range=(start_date,today)) # expense and income records

            week_total_expense = 0
            week_total_sales = 0
            week_other_income = 0
            week_net_balance =0 
            # Extract product info
            product_counter = Counter()
            for summary in week_data:
                week_total_expense += summary.total_expenses
                week_total_sales += summary.total_sales
                week_other_income += summary.other_income
                week_net_balance += summary.net_balance
                for product in summary.top_products.all():
                    product_counter[product.product_name] += product.quantity

            # Get top 50 products
            top_products = [ {'product': name, 'quantity': qty} for name, qty in product_counter.most_common(50) ]
            
            # Calculate profit and profit_margin safely
            profit = week_total_sales - week_total_expense
            profit_margin = (
                (profit / week_total_sales * Decimal('100.00')) if week_total_sales > 0 else Decimal('0.00')
            )

            def roi():
                if week_total_expense > 0:
                    roi_percent = ((profit) / week_total_expense) * Decimal('100.00')
                    return round(roi_percent, 2)
                return Decimal('0.00')
            week_data_summary = {
                'total_sales':week_total_sales,
                'total_expenses':week_total_expense,
                'other_income':week_other_income,
                'net_balance':week_net_balance,
                'profit':profit,
                'profit_margin':round(profit_margin,2),
                'roi':roi()
            }
            return [week_data_summary,top_products,week_orders,records]
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], [],[]]

    def get_monthly_finance_data(self, shop, month, year,*args, **kwargs):
        """ Helper function to get monthly finance data (revenue and expenses). """
        try:
            month_data = MonthlyFinanceSummary.objects.filter(shop=shop,recorded_at__month=month,recorded_at__year=year).first()
            month_orders = Order.objects.filter(shop=shop,order_at__month=month,order_at__year=year)
            records = FinanceRecord.objects.filter(shop=shop,create_at__month=month,create_at__year=year) # expense and income records

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
            return [month_data,top_products,month_orders,records]
        except Exception as e:
            print("Error in get_month_finance_data:", e)
            return [[], [], [],[]]
    
    def get_year_finance_data(self, shop, year,*args, **kwargs):
        """ Helper function to get year finance data (revenue and expenses). """
        try:
            year_data = MonthlyFinanceSummary.objects.filter(shop=shop,year=year)
            year_orders = Order.objects.filter(shop=shop,order_at__year=year)
            records = FinanceRecord.objects.filter(shop=shop,create_at__year=year) # expense and income records

            year_total_expense = 0
            year_total_sales = 0
            year_other_income = 0
            year_net_balance =0 
            # Extract product info
            product_counter = Counter()
            for summary in year_data:
                year_total_expense += summary.total_expenses
                year_total_sales += summary.total_sales
                year_other_income += summary.other_income
                year_net_balance += summary.net_balance
                for product in summary.top_products.all():
                    product_counter[product.product_name] += product.quantity

            # Get top 50 products
            top_products = [ {'product': name, 'quantity': qty} for name, qty in product_counter.most_common(50) ]
            
            # Calculate profit and profit_margin safely
            profit = year_total_sales - year_total_expense
            profit_margin = (
                (profit / year_total_sales * Decimal('100.00')) if year_total_sales > 0 else Decimal('0.00')
            )

            def roi():
                if year_total_expense > 0:
                    roi_percent = ((profit) / year_total_expense) * Decimal('100.00')
                    return round(roi_percent, 2)
                return Decimal('0.00')
            
            year_data_summary = {
                'total_sales':year_total_sales,
                'total_expenses':year_total_expense,
                'other_income':year_other_income,
                'net_balance':year_net_balance,
                'profit':profit,
                'profit_margin':round(profit_margin,2),
                'roi':roi
            }
            return [year_data_summary,top_products,year_orders,records]
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], [],[]]
    
    def tota_overview_finance_data(self,shop,*args, **kwargs):
        """ Helper function to get monthly finance data (revenue and expenses). """
        try:
            total_data = MonthlyFinanceSummary.objects.filter(shop=shop)
            total_orders = Order.objects.filter(shop=shop)
            records = FinanceRecord.objects.filter(shop=shop) # expense and income records
            total_total_expense = 0
            total_total_sales = 0
            total_other_income = 0
            total_net_balance =0 
            # Extract product info
            product_counter = Counter()
            for summary in total_data:
                total_total_expense += summary.total_expenses
                total_total_sales += summary.total_sales
                total_other_income += summary.other_income
                total_net_balance += summary.net_balance
                for product in summary.top_products.all():
                    product_counter[product.product_name] += product.quantity

            # Get top 50 products
            top_products = [ {'product': name, 'quantity': qty} for name, qty in product_counter.most_common(50) ]
            
            # Calculate profit and profit_margin safely
            profit = total_total_sales - total_total_expense
            profit_margin = (
                (profit / total_total_sales * Decimal('100.00')) if total_total_sales > 0 else Decimal('0.00')
            )

            def roi():
                if total_total_expense > 0:
                    roi_percent = ((profit) / total_total_expense) * Decimal('100.00')
                    return round(roi_percent, 2)
                return Decimal('0.00')
            
            total_data_summary = {
                'total_sales':total_total_sales,
                'total_expenses':total_total_expense,
                'other_income':total_other_income,
                'net_balance':total_net_balance,
                'profit':profit,
                'profit_margin':round(profit_margin,2),
                'roi':roi
            }
            return [total_data_summary,top_products,total_orders,records]
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], [],[]]

class FinanceDashboard(LoginRequiredMixin,FinanceSummary,View):
    def get(self,request,*args, **kwargs):
        fullmonth = request.GET.get('fullmonth')
        week_search = request.GET.get('week')
        yesterday_search = request.GET.get('yesterday')
        month = request.GET.get('month')
        this_year = request.GET.get('year')
        total_overiew = request.GET.get('totaloveriew')

        year = datetime.now().year
        today = date.today()
        shop = request.user
        
        data = None
        if fullmonth:
            try:
                year_search, month_search = fullmonth.split('-')
            except ValueError:
                year_search = month_search = None
        else:
            year_search = month_search = None

        if month_search and year_search:
            data = self.get_monthly_finance_data(shop,month_search,year_search)
        elif year_search:
            data = self.get_year_finance_data(shop,year_search)
        elif this_year:
            data = self.get_year_finance_data(shop,year=year)
        elif total_overiew:
            data = self.tota_overview_finance_data(shop=shop)
        elif month:
            month_n = datetime.now().month
            data = self.get_monthly_finance_data(shop=shop,month=month_n,year=year)
        elif yesterday_search:
            yesterday = today - timedelta(days=1)
            data = self.get_daily_finance_data(shop,yesterday,year)
        elif week_search:
            data = self.get_week_finance_data(shop=shop)
        else:
            data = self.get_daily_finance_data(shop,today,year)

        monthly_summary = MonthlyFinanceSummary.objects.filter(shop=shop).order_by('-year','-month')


        paginator = Paginator(monthly_summary, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # income expense
        income, expense = (
            [item for item in data[3] if item.category == 'income'],
            [item for item in data[3] if item.category == 'expense']
        )

        context = {
            'monthly_summary': page_obj,
            'month': data[0] if data else None,
            'top_products': data[1] if data else None, 
            'order':data[2] if data else None,
            'expense':expense[:6],
            'income':income[:4],
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

class IncomeExpenseView(LoginRequiredMixin,View):
    def get(self,request):
        form = FinanceRecordForm()

        filter_search = request.GET['filter'] if request.GET else None
        if filter_search == 'income' or filter_search == 'expense':
            records = FinanceRecord.objects.filter(shop=request.user,category=filter_search).order_by('-create_at')
        else:
            records = FinanceRecord.objects.filter(shop=request.user).order_by('-create_at')

        context = {
            'form':form,
            'records':records
        }
        return render(request,'incomexpense.html',context)
    
    def post(self,request,*args, **kwargs):
        form = FinanceRecordForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.shop = request.user 
            data.save()
            return redirect('/finance/income-expense/')
        context = {
            'form':form,
        }
        return render(request,'incomexpense.html',context)


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
