from items.models import Order, OrderItem
from django.db.models.signals import post_save
from django.dispatch import receiver

from store.utils import generate_invoice


# ---------------------------------------------
# Signal: Triggered when a new order is created
# ---------------------------------------------
@receiver(post_save,sender=OrderItem)
def send_invoice_on_whatsapp(sender,instance,created,*args, **kwargs):
    if created:
        shop=instance.order.shop
        order = instance
        
        orders = Order.objects.get(order_id=order.order_id)

        products = OrderItem.objects.filter(order=orders.order_id)

        response = generate_invoice(order=orders,user=shop,products=products)
        


