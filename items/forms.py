from django import forms
from items.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['images', 'name', 'price','purchase_price', 'stock', 'rack']

