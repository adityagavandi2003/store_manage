import json
from django.http import JsonResponse
from django.utils.timezone import make_aware, get_current_timezone,now
from django.shortcuts import render,redirect
from django.views import View
from datetime import datetime,date,timedelta,time
from django.contrib.auth.mixins import LoginRequiredMixin
from finance.models import MonthlyFinanceSummary,DailyFinanceSummary
from django.db.models.functions import TruncWeek
from items.models import Order,OrderItem
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from collections import Counter
from finance.forms import FinanceRecordForm
from finance.models import FinanceRecord
from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate
import calendar

# Create your views here.

# store all finance summary here to access easily
class FinanceSummary:
    """Unified finance summary handler for day, week, month, and year."""
    def get_finance_data(self, shop, mode='daily', date=None, month=None, year=None):
        """
        mode: 'daily', 'weekly', 'monthly', 'yearly'
        date: required for 'daily' mode
        month, year: required for 'monthly' mode
        year: required for 'yearly' mode
        """
        try:
            tz = get_current_timezone()
            product_counter = Counter()

            if mode == 'daily':
                day = date or datetime.now(tz).date()
                start = make_aware(datetime.combine(day, time.min), timezone=tz)
                end = make_aware(datetime.combine(day, time.max), timezone=tz)

                summary = DailyFinanceSummary.objects.filter(shop=shop,recorded_at__range=(start, end)).first()
                orders = Order.objects.filter(shop=shop, order_at__range=(start, end))
                records = FinanceRecord.objects.filter(shop=shop, create_at__range=(start, end)).order_by('-create_at')[:5]

            elif mode == 'weekly':
                today = datetime.now(tz).date()
                start_of_week = today - timedelta(days=6)
                end_of_week = today + timedelta(days=1) 
                start_day = make_aware(datetime.combine(start_of_week, time.min), timezone=tz)
                end_day = make_aware(datetime.combine(end_of_week, time.max), timezone=tz)
                summaries = DailyFinanceSummary.objects.filter(shop=shop, recorded_at__range=(start_day, end_day))
                orders = Order.objects.filter(shop=shop, order_at__range=(start_day, end_day))
                records = FinanceRecord.objects.filter(shop=shop, create_at__range=(start_day, end_day)).order_by('-create_at')[:5]
                total_sales = sum(s.total_sales for s in summaries)
                total_expenses = sum(s.total_expenses for s in summaries)
                other_income = Decimal('0.00')  # Placeholder
                profit = total_sales - total_expenses
                profit_margin = (profit / total_sales * Decimal('100.00')) if total_sales > 0 else Decimal('0.00')
                roi = (profit / total_expenses * Decimal('100.00')) if total_expenses > 0 else Decimal('0.00')

                summary = {
                    'total_sales': total_sales,
                    'total_expenses': total_expenses,
                    'other_income': other_income,
                    'net_balance': total_sales + other_income - total_expenses,
                    'profit': profit,
                    'profit_margin': round(profit_margin, 2),
                    'roi': round(roi, 2)
                }

            elif mode == 'monthly':
                start_date = make_aware(datetime(year, month, 1))
                end_day = calendar.monthrange(year, month)[1]  # last day of the month
                end_date = make_aware(datetime(year, month, end_day, 23, 59, 59))
                summary = MonthlyFinanceSummary.objects.filter( shop=shop, recorded_at__range=(start_date, end_date)).first()
                orders = Order.objects.filter(shop=shop, order_at__range=(start_date, end_date))
                records = FinanceRecord.objects.filter(shop=shop, create_at__range=(start_date, end_date)).order_by('-create_at')[:5]

            elif mode == 'yearly':
                year = year or datetime.now(tz).year

                summaries = MonthlyFinanceSummary.objects.filter(shop=shop, year=year)
                orders = Order.objects.filter(shop=shop, order_at__year=year)
                records = FinanceRecord.objects.filter(shop=shop, create_at__year=year).order_by('-create_at')[:5]

                total_sales = summaries.aggregate(Sum('total_sales'))['total_sales__sum'] or Decimal('0.00')
                total_expenses = summaries.aggregate(Sum('total_expenses'))['total_expenses__sum'] or Decimal('0.00')
                other_income = summaries.aggregate(Sum('other_income'))['other_income__sum'] or Decimal('0.00')

                profit = total_sales - total_expenses
                profit_margin = (profit / total_sales * Decimal('100.00')) if total_sales > 0 else Decimal('0.00')
                roi = (profit / total_expenses * Decimal('100.00')) if total_expenses > 0 else Decimal('0.00')

                summary = {
                    'total_sales': total_sales,
                    'total_expenses': total_expenses,
                    'other_income': other_income,
                    'net_balance': total_sales + other_income - total_expenses,
                    'profit': profit,
                    'profit_margin': round(profit_margin, 2),
                    'roi': round(roi, 2)
                }

            elif mode == 'total':
                summaries = MonthlyFinanceSummary.objects.filter(shop=shop)
                orders = Order.objects.filter(shop=shop)
                records = FinanceRecord.objects.filter(shop=shop).order_by('-create_at')[:5]

                total_sales = summaries.aggregate(Sum('total_sales'))['total_sales__sum'] or Decimal('0.00')
                total_expenses = summaries.aggregate(Sum('total_expenses'))['total_expenses__sum'] or Decimal('0.00')
                other_income = summaries.aggregate(Sum('other_income'))['other_income__sum'] or Decimal('0.00')

                profit = total_sales - total_expenses
                profit_margin = (profit / total_sales * Decimal('100.00')) if total_sales > 0 else Decimal('0.00')
                roi = (profit / total_expenses * Decimal('100.00')) if total_expenses > 0 else Decimal('0.00')

                summary = {
                    'total_sales': total_sales,
                    'total_expenses': total_expenses,
                    'other_income': other_income,
                    'net_balance': total_sales + other_income - total_expenses,
                    'profit': profit,
                    'profit_margin': round(profit_margin, 2),
                    'roi': round(roi, 2)
                }

            else:
                raise ValueError("Invalid mode. Choose from 'daily', 'weekly', 'monthly', 'yearly'.")

            # Top 6 products
            products = OrderItem.objects.filter(order__in=orders)
            for product in products:
                product_counter[product.product_name] += product.quantity

            top_products = [
                {'product': name, 'quantity': qty}
                for name, qty in product_counter.most_common(6)
            ]
            return [summary, top_products, orders, records]

        except Exception as e:
            print("Error in get_finance_data:", e)
            return [None, [], [], []]

class FinanceDashboard(LoginRequiredMixin, FinanceSummary, View):
    def get(self, request, *args, **kwargs):
        # Get all query parameters
        fullmonth = request.GET.get('fullmonth')
        week_search = request.GET.get('week')
        yesterday_search = request.GET.get('yesterday')
        month = request.GET.get('month')
        this_year = request.GET.get('year')
        total_overview = request.GET.get('totaloveriew')

        shop = request.user
        today = now().date()
        year = now().year
        data = None
        search_context = {}

        if fullmonth:
            try:
                year_search, month_search = fullmonth.split('-')
                data = self.get_finance_data(shop=shop, mode='monthly', month=int(month_search), year=int(year_search))
                search_context = {'month': month_search, 'year': year_search}
            except ValueError:
                data = None
        elif week_search:
            data = self.get_finance_data(shop=shop, mode='weekly')
        elif yesterday_search:
            yesterday = today - timedelta(days=1)
            data = self.get_finance_data(shop=shop, mode='daily', date=yesterday)
        elif month:
            data = self.get_finance_data(shop=shop, mode='monthly', month=today.month, year=year)
        elif this_year:
            data = self.get_finance_data(shop=shop, mode='yearly', year=year)
        elif total_overview:
            data = self.get_finance_data(shop=shop, mode='total')
        else:
            data = self.get_finance_data(shop=shop, mode='daily', date=today)

        monthly_summary = MonthlyFinanceSummary.objects.filter(shop=shop).order_by('-year', '-month')
        paginator = Paginator(monthly_summary, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Separate income and expense
        income = [record for record in data[3] if record.category == 'income'][:4]
        expense = [record for record in data[3] if record.category == 'expense'][:6]

        context = {
            'monthly_summary': page_obj,
            'month': data[0] if data else None,
            'top_products': data[1] if data else None,
            'order': data[2] if data else None,
            'income': income,
            'expense': expense,
        }

        if search_context:
            context['search'] = search_context

        return render(request, 'financedashboard.html', context)

class RevenueChart(View):
    def get(self, request, *args, **kwargs):
        tz = get_current_timezone()
        shop = request.user
        today = datetime.now(tz).date()
        start_of_week = today - timedelta(days=6)
        end_of_week = today + timedelta(days=1) 

        # Get summaries grouped by day
        data = DailyFinanceSummary.objects.filter(
            shop=shop,
            recorded_at__range=(start_of_week,end_of_week)
        )
        
        # Prepare chart data
        labels = []
        profit_data = []
        sales_data = []
        expense_data = []

        for entry in data:
            month_number = entry.recorded_at.month
            day = f'{entry.recorded_at.day} {calendar.month_name[month_number]}'
            labels.append(day)
            profit_data.append(entry.profit if entry.profit > 0 else 0)
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
        tz = get_current_timezone()
        shop = request.user
        today = datetime.now(tz).date()
        start_of_week = today - timedelta(days=6)
        end_of_week = today + timedelta(days=1) 

        daily_orders = Order.objects.filter(shop=shop,order_at__range=(start_of_week,end_of_week))
        # Extract product info
        products = OrderItem.objects.filter(order__in=daily_orders)
        product_counter = Counter()
        for product in products:  
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
