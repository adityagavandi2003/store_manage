from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, Order
from store.utils import generate_invoice,download_file
from .tasks import send_whatsapp_invoice_task

@receiver(post_save, sender=OrderItem)
def send_invoice_on_whatsapp(sender, instance, created, **kwargs):
    if created:
        order = instance.order
        shop = order.shop
        products = OrderItem.objects.filter(order=order)

        # Generate invoice and get file URL or path
        invoice_url = generate_invoice(order=order, user=shop, products=products)
        # Extract only needed fields to pass to Celery (can't pass Django model instance)
        shop_data = {
            "shop_name":order.shop.username,
            "customer": order.customer,
            "customer_phone": order.customer_phone,
        }

        # Call the Celery task
        send_whatsapp_invoice_task.delay(order.order_id, shop_data)
