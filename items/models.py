from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
from decimal import Decimal
# Create your models here.

def uid():
    idd = uuid.uuid4()
    # Convert UUID to string before splitting
    sp = str(idd).split('-')
    return f'{sp[0]+sp[1]+sp[2]}'

# Unit choices
UNIT_CHOICES = [
    ('kg', 'Kilogram'),
    ('g', 'Gram'),
    ('l', 'Liter'),
    ('ml', 'Milliliter'),
    ('pcs', 'Pieces'),
]

#category choices
CATEGORY_CHOICES = [
    ("GROCERY", "Grocery"),
    ("DAILY_ESSENTIALS", "Daily Essentials"),
    ("SNACKS_AND_NAMKEEN", "Snacks & Namkeen"),
    ("BEVERAGES", "Beverages"),
    ("FRUITS_AND_VEGETABLES", "Fruits & Vegetables"),
    ("OILS_AND_GHEE", "Oils & Ghee"),
    ("SPICES", "Spices"),
    ("PERSONAL_CARE", "Personal Care"),
    ("HOME_CARE", "Home Care"),
    ("BABY_CARE", "Baby Care"),
    ("CLEANING_SUPPLIES", "Cleaning Supplies"),
    ("STATIONERY", "Stationery"),
    ("PLASTIC_PRODUCTS", "Plastic Products"),
    ("FURNITURE", "Furniture"),
    ("PET_CARE", "Pet Care"),
    ("KITCHENWARE", "Kitchenware"),
    ("COSMETICS", "Cosmetics"),
    ("ELECTRONICS", "Electronics"),
    ("TOYS", "Toys"),
    ("OTHERS", "Others")
]

# Conversion dictionary for units like kg to g, ml to l, etc.
CONVERISON_FACTOR = {
    ('kg', 'g'): 1000,
    ('g', 'kg'): 1 / 1000,
    ('l', 'ml'): 1000,
    ('ml', 'l'): 1 / 1000,
    ('kg', 'pcs'): 1,  
    ('pcs', 'kg'): 1,  
}

class Product(models.Model):
    product_id = models.CharField(primary_key=True, default=uid, editable=False, max_length=255)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=15, help_text='Sell Price', decimal_places=2)
    purchase_price = models.DecimalField(max_digits=15, help_text='Purchase Price', decimal_places=2)
    stock = models.FloatField(verbose_name='total_stock',default=1)
    stock_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    r_stock = models.FloatField(default=0, verbose_name='remaining_stock')
    r_stock_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg', verbose_name='remaining_stock_unit')
    images = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rack = models.CharField(max_length=50,null=True,blank=True)
    listed_by = models.ForeignKey(User, related_name='add_by_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHERS')

    def __str__(self):
        return self.name

    def convert_to_remaining_unit(self, quantity, unit):
        """
        Converts the quantity to the unit used by the product's remaining stock.
        Handles conversion between units like kg, g, ml, l, pcs, etc.
        """
        # If the unit is 'pcs', 
        if unit == 'pcs' and self.r_stock_unit == 'pcs':
            return quantity

        # If the unit is the same as the remaining stock unit, no conversion is needed
        if unit == self.r_stock_unit:
            return quantity

        # Check if the unit is supported for conversion
        key = (unit, self.r_stock_unit)
        if key in CONVERISON_FACTOR:
            factor = CONVERISON_FACTOR[key]
            return quantity * factor

        # Raise error if the conversion is not supported
        raise ValueError(f"Unsupported unit conversion from {unit} to {self.r_stock_unit}")
    
    def reduce_stock(self, quantity, unit):
        """
        Reduce the stock based on the quantity and unit provided. Converts units if necessary.
        Raises a ValueError if there is not enough stock available.
        """

        converted_quantity = self.convert_to_remaining_unit(quantity, unit)

        # Check if there is enough remaining stock
        if converted_quantity < self.r_stock:
            raise ValueError("Not enough stock available.")

        # Update the remaining stock
        self.r_stock -= float(converted_quantity)
        self.save()
    
    @property
    def profit_margin_on_product(self):
        if self.stock == 0:
            return Decimal('0.00')
        
        per_product_price = self.purchase_price / Decimal(self.stock)
        sell_revenue = Decimal(self.stock) * self.price
        
        if per_product_price == 0:
            return Decimal('0.00') 
        
        profit = sell_revenue - self.purchase_price
        profit_per_product = profit / Decimal(self.stock)
        profit_margin = (profit_per_product / self.price) * Decimal('100.00')
        return round(profit_margin,2)
    
    @property
    def display_remaining_stock(self):
        return f"{round(self.stock+self.r_stock, 2)} {self.r_stock_unit}"
    
    @property
    def stock_quantity_with_unit(self):
        return f'{round(self.stock,2)} {self.r_stock_unit}'

    @property
    def display_price(self):
        return f'₹{self.price}/{self.stock_unit}'
    
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
    payment_mode = models.CharField(max_length=50)
    order_at = models.DateTimeField(default=timezone.now)

    
    def __str__(self):
        return f"{self.order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10,help_text='Sell Price',decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    quantity = models.FloatField(default=1, verbose_name='quantity')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product_name}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only on first creation
            try:
                product = Product.objects.get(name=self.product_name)
                product.reduce_stock(self.quantity, self.unit)
            except Product.DoesNotExist:
                raise ValueError(f"Product with name {self.product_name} does not exist")

        super().save(*args, **kwargs)
    
    @property
    def stock_quantity_with_unit(self):
        return f'{round(self.product_price,2)} {self.unit}'

