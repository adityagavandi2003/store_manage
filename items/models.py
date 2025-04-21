from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.

def uid():
    idd = uuid.uuid4()
    # Convert UUID to string before splitting
    sp = str(idd).split('-')
    return f'#SALE00{sp[0]}'


class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    price = models.CharField(max_length=15,help_text='Sell Price')
    purchase_price = models.CharField(max_length=15,help_text='Purchase Price')
    stock = models.CharField(max_length=15)
    images = models.ImageField(upload_to='product_images/',blank=True,null=True)
    rack = models.CharField(max_length=50)
    listed_by = models.ForeignKey(User, related_name='add_by_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Customer(models.Model):
    name = models.CharField(max_length=50,null=True,blank=True)
    phone_number = models.CharField(max_length=10,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    order_id = models.CharField(primary_key=True, default=uid, editable=False, max_length=255)
    shop = models.ForeignKey(User, related_name='store_owner', on_delete=models.CASCADE)
    customer = models.CharField(max_length=50,default='Guest')
    customer_phone = models.CharField(max_length=15,blank=True,null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # razorpay 
    razorpay_order_id = models.CharField(max_length=255,blank=True,null=True )
    razorpay_payment_id = models.CharField(max_length=255,blank=True,null=True )
    razorpay_signature = models.CharField(max_length=50,blank=True,null=True )
    
    is_paid = models.BooleanField(default=False)
    payment_mode = models.CharField( max_length=50)
    order_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_price = models.CharField(max_length=15,help_text='Sell Price')
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name}"