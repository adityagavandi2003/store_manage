import calendar
from collections import Counter
from celery import shared_task
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import date, datetime, time,timedelta
from time import sleep
from django.utils.timezone import make_aware, get_current_timezone,now
from finance.models import DailyFinanceSummary, FinanceRecord, MonthlyFinanceSummary
from items.models import Order, OrderItem, Product
from store.utils import to_decimal_safe,create_notification
from khatabook.models import KhataBook
from decimal import Decimal
from django.contrib.auth import get_user_model
from celery.utils.log import get_task_logger
from users.models import Notification

tz = get_current_timezone()
User = get_user_model()
logger = get_task_logger(__name__)

def is_last_day_of_month(date_obj):
    return (date_obj + timedelta(days=1)).month != date_obj.month

@shared_task
def handle_order_finance(order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        shop = order.shop
        order_date = order.order_at.date() if order.order_at else datetime.now(tz).date()
        start = make_aware(datetime.combine(order_date, time(6, 0)), timezone=tz)

        finance, _ = DailyFinanceSummary.objects.get_or_create(
            shop=shop,
            recorded_at=start,
            defaults={
                'total_sales': Decimal('0.00'),
                'total_expenses': Decimal('0.00'),
                'other_income': Decimal('0.00'),
            }
        )

        finance.total_sales = to_decimal_safe(finance.total_sales) + to_decimal_safe(order.total_amount)
        finance.calculate_profit()
        finance.save()

        if order.payment_mode == 'KhataBook':
            KhataBook.objects.get_or_create(
                shop=shop,
                order=order,
                customer_name=order.customer,
                total_khata_amount=order.total_amount,
            )
        
    except Exception as e:
        print(f"[CELERY ERROR] Failed processing order {order_id}: {e}")

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_month_finance(self,shop_id):
    try:
        today = now().date()
        if not is_last_day_of_month(today):
            logger.info(f"Skipped for shop {shop_id}: Not last day of month.")
            return
        
        shop = User.objects.get(id=shop_id)
        start_date = today.replace(day=1)
        end_date = today

        summary_qs = DailyFinanceSummary.objects.get(shop=shop.id, recorded_at__range=(start_date, end_date))

        total_sales = summary_qs.aggregate(Sum('total_sales'))['total_sales__sum'] or Decimal('0.00')
        total_expenses = summary_qs.aggregate(Sum('total_expenses'))['total_expenses__sum'] or Decimal('0.00')
        other_income = summary_qs.aggregate(Sum('other_income'))['other_income__sum'] or Decimal('0.00')

        profit = total_sales - total_expenses
        profit_margin = (profit / total_sales * Decimal('100.00')) if total_sales > 0 else Decimal('0.00')

        MonthlyFinanceSummary.objects.get_or_create(
            shop=shop,
            month=today.month,
            year=today.year,
            defaults={
                'total_sales': total_sales,
                'total_expenses': total_expenses,
                'other_income': other_income,
                'profit': profit,
                'profit_margin': profit_margin,
                'recorded_at': now(),
            }
        )
        logger.info(f"Monthly finance created for shop {shop.id}")
        create_notification(shop.id, "Monthly finance summary generated.")
        
    except Exception as e:
        logger.error(f"Error processing finance for shop {shop_id}: {str(e)}")
        self.retry(exc=e)

@shared_task
def create_month_finance_for_all_shops():
    for shop in User.objects.all():
        create_month_finance.delay(shop.id)

