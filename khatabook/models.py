from decimal import Decimal
from django.utils import timezone
from django.db import models
from items.models import Order
from django.contrib.auth.models import User
# Create your models here.

class KhataBook(models.Model):
    shop = models.ForeignKey(User,related_name='shop_owner', on_delete=models.CASCADE)
    order = models.ForeignKey(Order,related_name='khatabook_orders',on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    total_khata_amount = models.DecimalField(max_digits=5, decimal_places=2,default=0.00,blank=True,null=True)
    paid_amount = models.DecimalField(max_digits=5, decimal_places=2,default=0.00,blank=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.order.order_id
    
    @property
    def remaining_amount(self):
        total = self.total_khata_amount or Decimal('0.00')
        paid = self.paid_amount or Decimal('0.00')
        remaining_balance = total - paid
        return remaining_balance.quantize(Decimal('0.01'))
    
    