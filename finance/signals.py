from datetime import date, datetime, time
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import make_aware, get_current_timezone
from finance.models import DailyFinanceSummary, FinanceRecord
from items.models import Order, Product
from store.utils import to_decimal_safe
from khatabook.models import KhataBook

tz = get_current_timezone()

# ---------------------------------------------
# Signal: Triggered when a new order is created
# ---------------------------------------------
@receiver(post_save, sender=Order)
def update_finance_on_order(sender, instance, created, **kwargs):
    if created:
        shop = instance.shop
        order_date = instance.order_at.date() if instance.order_at else datetime.now(tz).date()
        start = make_aware(datetime.combine(order_date, time(6, 0)), timezone=tz)

        # Get or create the daily finance record
        finance, created = DailyFinanceSummary.objects.get_or_create(
            shop=shop,
            recorded_at=start,
            defaults={
                'total_sales': Decimal('0.00'),
                'total_expenses': Decimal('0.00'),
                'other_income': Decimal('0.00'),
            }
        )

        # Update total sales and calculate profit
        finance.total_sales = to_decimal_safe(finance.total_sales) + to_decimal_safe(instance.total_amount)
        finance.calculate_profit()
        finance.save()
        try:
          if instance.payment_mode == 'KhataBook':
              KhataBook.objects.get_or_create(
                  shop=shop,
                  order=instance,
                  customer_name=instance.customer,
                  total_khata_amount=instance.total_amount,
              )
        except Exception as e:
          print('An exception occurred',e)

# ---------------------------------------------
# Signal: Triggered when a new product is added
# ---------------------------------------------
@receiver(post_save, sender=Product)
def update_finance_on_product(sender, instance, created, **kwargs):
    shop = instance.listed_by
    created_date = instance.created_at.date() if hasattr(instance, 'created_at') else date.today()
    start = make_aware(datetime.combine(created_date, time(6, 0)), timezone=tz)

    # Get or create the daily finance record
    finance, _ = DailyFinanceSummary.objects.get_or_create(
        shop=shop,
        recorded_at=start,
        defaults={
            'total_sales': Decimal('0.00'),
            'total_expenses': Decimal('0.00'),
            'other_income': Decimal('0.00'),
        }
    )

    # Only add to expenses if the product is newly created
    if created:
        finance.total_expenses = to_decimal_safe(finance.total_expenses) + to_decimal_safe(instance.purchase_price)
        finance.calculate_profit()

# ---------------------------------------------
# Signal: Triggered when a product is updated
# ---------------------------------------------
@receiver(post_save, sender=Product)
def update_finance_on_restock(sender, instance, created, **kwargs):
    if not created:  # Only handle updates
        try:
            previous_instance = Product.objects.get(pk=instance.pk)
        except Product.DoesNotExist:
            return  # Skip if previous doesn't exist

        # Check if restock occurred with price change (purchase_price changed and quantity increased)
        price_changed = instance.purchase_price != previous_instance.purchase_price
        stock_increased = instance.stock > previous_instance.stock

        if price_changed and stock_increased:
            shop = instance.listed_by
            update_date = datetime.now(tz).date()
            start = make_aware(datetime.combine(update_date, time(6, 0)), timezone=tz)
            end = make_aware(datetime.combine(update_date, time.max), timezone=tz)

            # Fetch or create today's finance summary
            finance = DailyFinanceSummary.objects.filter(shop=shop, recorded_at__range=(start, end)).first()
            if not finance:
                finance = DailyFinanceSummary.objects.create(
                    shop=shop,
                    recorded_at=start,
                    total_sales=Decimal('0.00'),
                    total_expenses=Decimal('0.00'),
                    other_income=Decimal('0.00'),
                )

            # Calculate the cost difference for the restocked units
            restocked_quantity = instance.stock - previous_instance.stock
            price_difference = instance.purchase_price - previous_instance.purchase_price
            added_expense = price_difference * restocked_quantity

            # Update expense and profit
            finance.total_expenses += to_decimal_safe(added_expense)
            finance.calculate_profit()
            finance.save()

# ---------------------------------------------
# Signal: Triggered when a new income or expense is created
# ---------------------------------------------
@receiver(post_save, sender=FinanceRecord)
def update_finance_on_financerecord(sender, instance, created, *args, **kwargs):
    if created:
        shop = instance.shop
        category = instance.category
        created_date = instance.create_at.date() if hasattr(instance, 'create_at') else date.today()
        start = make_aware(datetime.combine(created_date, time(6, 0)), timezone=tz)

        # Get or create the daily finance record
        finance, created = DailyFinanceSummary.objects.get_or_create(
            shop=shop,
            recorded_at=start,
            defaults={
                'total_sales': Decimal('0.00'),
                'total_expenses': Decimal('0.00'),
                'other_income': Decimal('0.00'),
            }
        )

        # Update based on the category (income or expense)
        if category == 'expense':
            finance.total_expenses = to_decimal_safe(finance.total_expenses) + to_decimal_safe(instance.amount)
        elif category == 'income':
            finance.other_income = to_decimal_safe(finance.other_income) + to_decimal_safe(instance.amount)
        else:
            print('Error: Invalid category')

        # Recalculate profit
        finance.calculate_profit()
        finance.save()