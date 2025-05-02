from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal
# Create your models here.

def uid():
    idd = uuid.uuid4()
    # Convert UUID to string before splitting
    sp = str(idd).split('-')
    return f'{sp[0]+sp[1]+sp[2]}'

def productid():
    idd = uuid.uuid4()
    sp = str(idd).split('-')
    return f'{sp[4]}'

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
    product_id = models.CharField(primary_key=True, default=productid, editable=False)
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
    created_at = models.DateTimeField(auto_now_add=True)
    
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
        # Convert the requested quantity to the unit used for remaining stock
        converted_quantity = self.convert_to_remaining_unit(quantity, unit)

        # Check if there is enough remaining stock
        if converted_quantity < self.r_stock:
            raise ValueError("Not enough stock available.")

        # Update the remaining stock
        self.r_stock -= float(converted_quantity)
        self.save()

    # convert units
    def restock(self, quantity, unit):
        """
        Restock logic that allows adding quantities based on unit (including fractions for non-'pcs' units).
        """
        # If unit is pcs, we can only add whole numbers of pieces
        if unit == 'pcs':
            if quantity < 1 or quantity != int(quantity):
                raise ValueError("Only whole pieces can be added.")
            self.stock += quantity
            self.r_stock += quantity
        else:
            # For weight/volume units (kg, g, l, ml), fractional quantities can be added
            valid_quantities = [0.25, 0.5, 0.75, 1, 1.25]  # Allowed fractional increments

            if quantity < 0.25:
                raise ValueError("Minimum quantity for restocking is 0.25.")
            
            if quantity not in valid_quantities and quantity % 0.25 != 0:
                raise ValueError("Only quantities like 0.25, 0.5, 0.75, 1, 1.25... can be added.")

            # If the quantity is valid, add to stock
            converted_qty = self.convert_to_remaining_unit(quantity, unit)
            self.stock += converted_qty
            self.r_stock += converted_qty
        
        self.save()
        
    @property
    def display_remaining_stock(self):
        return f"{round(self.stock+self.r_stock, 2)} {self.r_stock_unit}"
    
    @property
    def stock_quantity_with_unit(self):
        return f'{round(self.stock,2)} {self.r_stock_unit}'

    @property
    def display_price(self):
        # If the product is in 'pcs', the price will be per piece
        if self.stock_unit == 'pcs':
            return f"₹{self.price} per piece"
        # If the product is in other units like kg, g, ml, l, it displays the price for that unit
        return f"₹{self.price} per {self.stock_unit}"
    
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
    product_price = models.DecimalField(max_digits=10,help_text='Sell Price',decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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

