from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from items.forms import ProductForm
from items.models import Product,Order,OrderItem
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import uuid
from django.db import transaction
# Create your views here.


def uid():
    idd = uuid.uuid4()
    # Convert UUID to string before splitting
    sp = str(idd).split('-')
    return sp[0]


class Home(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(listed_by=request.user).order_by('-created_at')
        cart = request.session.get('cart')
        context = {'products': product,'cart':cart}
        return render(request, 'home.html', context)


class Dashboard(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        today = timezone.now()
        thirty_days_ago= today-timedelta(days=30)
        product = Product.objects.filter(
            listed_by=request.user,created_at__date__gte=thirty_days_ago).order_by('-created_at')
                
        orders  = Order.objects.filter(shop=request.user,order_at__date__gte=thirty_days_ago).order_by('-order_at')
        total = orders.aggregate(total_amount=Sum('total_amount'))['total_amount'] or Decimal(0)

        due_payments = orders.filter(is_paid=False)
        due_amount = due_payments.aggregate(total_amount=Sum('total_amount'))['total_amount'] or Decimal(0)
        paid_amount = total - due_amount if due_amount is not None else total

        order_recieved = orders.count()- due_payments.count()
        
        paginator = Paginator(product, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'products':page_obj,
            'total':total,
            "due_payments":due_payments,
            'due_amount':due_amount,
            'paid_amount':paid_amount,
            'order_recieved':order_recieved,    
        }
        return render(request, 'dashboard.html', context)


class View_Product(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(
            listed_by=request.user).order_by('-created_at')
        paginator = Paginator(product, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'page_obj': page_obj}
        return render(request, 'product/viewproduct.html', context)


class Add_Product(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ProductForm()
        product = Product.objects.filter(
            listed_by=request.user).order_by('-created_at')[:5]

        context = {'form': form, 'products': product}
        return render(request, 'product/addproduct.html', context)

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.listed_by = request.user
            product.save()
            messages.success(request, '✅ Product added successfully!')
            return redirect('/product/add/')
        context = {'form': form, }
        return render(request, 'product/addproduct.html', context)


class Edit_Product(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        context = {'form': form, 'product': product}
        return render(request, 'product/editproduct.html', context)

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Product update successfully!')
            return redirect('/dashboard/')
        context = {'form': form, 'product': product}
        return render(request, 'product/editproduct.html', context)


class Delete_Product(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        if product:
            product.delete()
            messages.success(request, '✅ Product delete successfully!')
            return redirect('/dashboard/')

class Checkout(View):
    """Displays the user's shopping cart."""
    def get(self,request,*args, **kwargs):
        cart = request.session.get("cart",{})
        cart_items = []
        total = 0

        if cart:
            for product_id , product_data in cart.items():
                try:
                    product = Product.objects.get(pk=product_id)
                    quantity = product_data['quantity']
                    price = product_data['price'].split('/')[0]
                    subtotal = int(quantity) * float(price)
                    total += subtotal
                    cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
                except Product.DoesNotExist:
                    del cart[product_id]
                    request.session['cart']=cart
        else:
            return redirect('/')
                
        context = {'cart_items': cart_items, 'cart_total': total}
        return render(request, 'checkout.html',context)

class AddToCart(View):
    """Adds a product to the user's shopping cart (using session)."""
    def get(self, request, pk, *args, **kwargs):
        quantity = int(request.GET.get('quantity', 1))
        product = get_object_or_404(Product, pk=pk)
        cart = request.session.get('cart', {})
        if pk in cart:
            cart[pk]['quantity'] += quantity
        else:
            cart[pk] = {'quantity': quantity, 'price': str(product.price)}
        request.session['cart'] = cart
        messages.success(request, f"{quantity} x {product.name} added to cart.")
        return redirect('/')

class DeleteCart(View):
    def get(self,request,pk,*args, **kwargs):
        cart = request.session.get('cart',{})
        if pk in cart:
            del cart[pk]
            request.session['cart']=cart
            messages.success(request,'Item removed from cart')
        else:
            messages.warning(request,"Item not found in cart")        
        return redirect('/checkout/')

class ClearCart(View):
    def get(self,request,*args, **kwargs):
        cart = request.session.get('cart',{})
        if cart:
            del cart
            request.session['cart']={}
            messages.success(request,'Cart clear successfully')
        else:
            messages.warning(request,"No cart found")        
        return redirect('/')


class SalesOverview(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        today = timezone.now()
        thirty_days_ago= today-timedelta(days=30)
        
        # filter products on paid or unpaid
        filter_value = request.GET.get('filter')

        if filter_value == 'paid':  # Paid
            orders = Order.objects.filter(shop=request.user,is_paid=True,order_at__date__gte=thirty_days_ago).order_by('-order_at')
        elif filter_value == 'unpaid':  # Unpaid
            orders = Order.objects.filter(shop=request.user,is_paid=False,order_at__date__gte=thirty_days_ago).order_by('-order_at')
        else: # all
            orders = Order.objects.filter(shop=request.user,order_at__date__gte=thirty_days_ago).order_by('-order_at')
        
        total_order = orders.count()
        total_amount = orders.aggregate(total_amount=Sum('total_amount'))['total_amount']
        due_payments = orders.filter(is_paid=False)
        due_amount = due_payments.aggregate(total_amount=Sum('total_amount'))['total_amount']
        paid_amount = total_amount - due_amount if due_amount is not None else total_amount

        order_recieved = orders.count()- due_payments.count()
        

        # next and previous btn
        paginator = Paginator(orders, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        
        context = {
            'orders':page_obj,
            'total_amount':total_amount,
            'total_order':total_order,
            "due_payments":due_payments,
            'due_amount':due_amount,
            'paid_amount':paid_amount,
            'order_recieved':order_recieved,    
        }
        return render(request,'salesoverview.html',context)
    

class ItemsOrder(LoginRequiredMixin,View):
    @transaction.atomic  # Ensures the order is created fully or not at all
    def post(self,request,*args, **kwargs):
        cart = request.session.get('cart',{})

        payment_method = request.POST.get('payment_method')
        shop_owner = request.user
        total = Decimal('0.00')
        order_items = []

        for product_id,item in cart.items():
            try:
                product = Product.objects.get(pk=product_id)
                product_price = item['price'].split('/')[0]
                subtotal = item['quantity'] * Decimal(product_price)
                total += subtotal
                order_items.append({
                    'product': product,
                    'product_name': product.name,
                    'product_price': item['price'],
                    'quantity': item['quantity'],
                    'subtotal': subtotal,
                })
            except Product.DoesNotExist:
                continue
        
        is_paid = True if payment_method != 'online' else False
        order = Order.objects.create(
            order_id=f'#SALE00{uid()}',
            shop=shop_owner,
            customer='Guest1',
            total_amount=total,
            is_paid=is_paid,
            payment_mode=payment_method
        )

        for items in order_items:
            OrderItem.objects.create(
                order = order,
                product_name=items['product_name'],
                product_price=items['product_price'],
                quantity=items['quantity'],
                subtotal=items['subtotal']
            )

        # Clear cart
        request.session['cart'] = {}
        messages.success(request,'Order Completed')
        return render(request, 'orders/order_success.html', {'order': order})

        
        