from django.db import models
from items.models import Order
from django.contrib.auth.models import User
# Create your models here.

class KhataBook(models.Model):
    shop = models.ForeignKey(User,related_name='shop_owner', on_delete=models.CASCADE)
    order = models.ForeignKey(Order,related_name='khatabook_orders',on_delete=models.CASCADE)
    total_khata_amount = models.DecimalField(max_digits=5, decimal_places=2,default=0.00,blank=True,null=True)
    paid_amount = models.DecimalField(max_digits=5, decimal_places=2,default=0.00,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order.order_id
    
    @property
    def remaing_amount(self):
        remaing_balance = self.total_khata_amount - self.paid_amount
        return remaing_balance