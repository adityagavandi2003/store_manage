import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from finance.models import DailyFinanceSummary
from items.forms import ProductForm
from items.models import Product,Order,OrderItem
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils import timezone
from collections import Counter
from decimal import Decimal
import uuid
import razorpay
from store import settings
from store.utils import generate_invoice
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def uid():
    idd = uuid.uuid4()
    # Convert UUID to string before splitting
    sp = str(idd).split('-')
    return f'{sp[0]+sp[1]+sp[2]}'

# client for razorpay
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECREATE_KEY))

class Home(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(listed_by=request.user).order_by('-created_at')
        cart = request.session.get('cart')
        context = {'products': product,'cart':cart}
        return render(request, 'home.html', context)


class Dashboard(LoginRequiredMixin, View):
    def get_daily_finance_data(self,shop,day,*args, **kwargs):
        """ Helper function to get daily finance data (revenue and expenses). """
        try:
            year = datetime.now().year
            daily_data = DailyFinanceSummary.objects.filter(shop=shop,day=day).first()
            daily_orders = Order.objects.filter(shop=shop,order_at__day=day,order_at__year=year)
            # Extract product info
            daily_products = [product for product in daily_data.top_products.all()] if daily_data else []
            product_counter = Counter()
            for product in daily_products:  
                product_counter[product.product_name] += product.quantity

            # Get top 50 products
            top_products = [
                {'product': name, 'quantity': qty}
                for name, qty in product_counter.most_common(50)
            ]
            return [daily_data,top_products,daily_orders]
        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [[], [], []]
            
    def get(self, request, *args, **kwargs):
        today = timezone.now()
        thirty_days_ago= today-timedelta(days=30)
        product = Product.objects.filter(
            listed_by=request.user,created_at__date__gte=thirty_days_ago).order_by('-created_at')
        shop = request.user
        day = datetime.now().day
        data = self.get_daily_finance_data(shop,day)

        paginator = Paginator(product, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'products':page_obj,  
            'daily': data[0] if data else '',
            'top_products': data[1] if data else '', 
            'order':data[2] if data else '',
        }
        return render(request, 'dashboard.html', context)


class View_Product(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product = Product.objects.filter(
            listed_by=request.user).order_by('-created_at')
        paginator = Paginator(product, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {'products': page_obj}
        return render(request, 'product/viewproduct.html', context)

class ProductView(LoginRequiredMixin,View):
    def get(self,request,pk,*args, **kwargs):
        product = get_object_or_404(Product,pk=pk)
        context = {
            'product':product,
        }
        return render(request,'product/productview.html',context)

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
            product.r_stock_unit = product.stock_unit
            product.save()
            messages.success(request, '✅ Product added successfully!')
            return redirect('/product/add/')
        else:
            messages.error(request,'Product failed to add')
            return redirect('/product/add/')

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
        total = Decimal('0.00')

        if cart:
            for product_id , product_data in cart.items():
                try:
                    product = Product.objects.get(pk=product_id)
                    quantity = product_data['quantity']
                    price = product_data['price']
                    subtotal = Decimal(quantity) * Decimal(price)
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
        quantity = float(request.GET.get('quantity', 1))
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

@method_decorator(csrf_exempt,name='dispatch')
class OfflinePaymentView(LoginRequiredMixin,View):
    def post(self,request):
        cart = request.session.get('cart',{})

        data = json.loads(request.body)
        mode = data.get('mode')  # either 'Offline' or 'KhataBook'
        customer_name = data.get('name')
        customer_phone = data.get('phone')

        shop_owner = request.user
        total = Decimal('0.00')
        order_items = []
        for product_id,item in cart.items():
            try:
                product = Product.objects.get(pk=product_id)
                product_price = item['price']
                subtotal = Decimal(item['quantity']) * Decimal(product_price)
                total += subtotal
                order_items.append({
                    'product': product,
                    'product_name': product.name,
                    'product_price': Decimal(item['price']),
                    'quantity': Decimal(item['quantity']),
                    'subtotal': subtotal,
                })

            except Product.DoesNotExist:
                continue

        order = Order.objects.create(
            order_id=uid(),
            shop=shop_owner,
            customer=customer_name,
            customer_phone=customer_phone,
            total_amount=total,
            is_paid=(mode == "Offline"),
            payment_mode=mode
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
        if mode=='Offline':
            messages.success(request,'Order Completed')
        else:
            messages.success(request,'Add in Khatabook')
        return JsonResponse({'success': True})
    
@method_decorator(csrf_exempt,name='dispatch')
class OnlinePaymentView(LoginRequiredMixin,View):
    def post(self,request):
        cart = request.session.get('cart',{})

        data = json.loads(request.body)
        customer_name = data.get('name')
        customer_phone = data.get('phone')
        
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
    
        
        order_data = {
            'amount':int(total * 100), # paise
            'currency':"INR",
            'payment_capture':"1",
        }
        razorpay_order = client.order.create(order_data)
        order = Order.objects.create(
            order_id=uid(),
            shop=shop_owner,
            total_amount=total,
            customer = customer_name,
            customer_phone = customer_phone,
            payment_mode="Online",
            razorpay_order_id=razorpay_order['id'],
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
        return JsonResponse({
            "order_id": razorpay_order['id'],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            'products_name': [item['product_name'] for item in order_items],
            'shop_owner': shop_owner.username,
            "amount": float(total),
            "razorpay_callback_url": settings.RAZORPAY_CALLBACK_URL
        })

@method_decorator(csrf_exempt,name='dispatch')
class PaymentCallbackView(View):
    def post(self,request):
        if "razorpay_signature" in request.POST:
            order_id = request.POST.get('razorpay_order_id')
            payment_id = request.POST.get('razorpay_payment_id')
            signature = request.POST.get('razorpay_signature')
            order = get_object_or_404(Order,razorpay_order_id=order_id)

            if client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }):
                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.is_paid = True
                order.save()
                
                messages.success(request,'Order Completed')
                return render(request, 'orders/order_success.html')
            else:
                order.is_paid = False
                order.save()
                messages.success(request,'Order Failed')
                return render(request, 'orders/order_failed.html')
        else:
            messages.success(request,'Order Failed')
            return render(request, 'orders/order_failed.html')
        

class OrderSucessView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'orders/order_success.html')
    
class OrderFailedView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'orders/order_failed.html')
    

class InvoiceView(LoginRequiredMixin,View):
    def get(self,request,pk,*args, **kwargs):
        data = get_object_or_404(Order,pk=pk)
        products = OrderItem.objects.filter(order=data.order_id)

        context = {
            'data':data,
            'products':products,
        }
        return render(request,'invoice/invoice.html',context)
    
    def post(self,request,*args, **kwargs):
        pk = request.POST['id']
        data = get_object_or_404(Order,pk=pk)
        products = OrderItem.objects.filter(order=data.order_id)
        try:
            response = generate_invoice(order=data,user=request.user.username,products=products)
            messages.success(request,'Pdf successfully generated')
            return response
        except:
            messages.error(request,'An error occurs while generating the PDF.')
            return redirect(f'/invoice/{pk}')