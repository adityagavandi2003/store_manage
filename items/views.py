import json
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from finance.models import DailyFinanceSummary
from items.forms import ProductForm
from items.models import Product,Order,OrderItem
from django.db.models import Sum
from django.core.paginator import Paginator
from datetime import date, datetime, timedelta
from django.utils import timezone
from collections import Counter
from decimal import Decimal
from users.models import Notification
from django.contrib.auth.models import User
import uuid
import razorpay
from store import settings
from store.utils import generate_invoice,download_file,compress_image_to_target_size
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

class SearchView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        name = request.GET.get('search')
        order = Order.objects.filter(customer=name).values()
        return JsonResponse(list(order), safe=False)

class Dashboard(LoginRequiredMixin, View):
    def get_daily_finance_data(self, shop, day, *args, **kwargs):
        try:
            daily_data = DailyFinanceSummary.objects.filter(
                shop=shop,
                recorded_at__gte=day
            ).first()
            daily_orders = Order.objects.filter(
                shop=shop,
                order_at__gte=day
            )
            products = OrderItem.objects.filter(order__in=daily_orders).order_by('-quantity')
            return [daily_data, products, daily_orders]

        except Exception as e:
            print("Error in get_daily_finance_data:", e)
            return [None, [], []]

    def get(self, request, *args, **kwargs):
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)

        product = Product.objects.filter(
            listed_by=request.user,
            created_at__gte=thirty_days_ago
        ).order_by('-created_at')

        shop = request.user
        day = date.today()
        data = self.get_daily_finance_data(shop, day)

        product_map = {}
        for item in data[1]:
            name = item.product_name
            price = item.product_price
            quantity = item.quantity
            if name in product_map:
                product_map[name]['quantity'] += quantity
                product_map[name]['subtotal'] += price * Decimal(quantity)
            else:
                product_map[name] = {
                    'quantity': quantity,
                    'price': price,
                    'subtotal': price * Decimal(quantity)
                }

        sorted_products = sorted(
            [(name, details['quantity'], details['price'], details['subtotal'])
             for name, details in product_map.items()],
            key=lambda x: x[1],
            reverse=True
        )

        paginator = Paginator(product, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        top_product_paginator = Paginator(sorted_products, 10)
        top_product_page_no = request.GET.get('top_page', 1)
        top_product = top_product_paginator.get_page(top_product_page_no)

        context = {
            'products': page_obj,
            'daily': data[0],
            'top_products': top_product,
            'order': data[2],
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
            # Compress the image before assigning
            uploaded_image = form.cleaned_data['images']
            compressed_image = compress_image_to_target_size(uploaded_image, target_kb=100)
            product.images.save(uploaded_image.name, compressed_image, save=False)
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
        r_stock = product.stock + product.r_stock
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            data = form.save(commit=False)    
            if r_stock == 0:
                data.r_stock = 0
                data.save()
            else:
                data.r_stock = 0
                data.stock += r_stock
                data.save()
            product.created_at = timezone.now()
            product.save()
            messages.success(request, '✅ Product update successfully!')
            return redirect('/products/')
        else:
            messages.error(request,'Something wrong')
            return redirect(f'/product/edit/{pk}')

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
            orders = Order.objects.filter(shop=request.user,is_paid=True,order_at__gte=thirty_days_ago).order_by('-order_at')
        elif filter_value == 'unpaid':  # Unpaid
            orders = Order.objects.filter(shop=request.user,is_paid=False,order_at__gte=thirty_days_ago).order_by('-order_at')
        else: # all
            orders = Order.objects.filter(shop=request.user,order_at__gte=thirty_days_ago).order_by('-order_at')
        
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
                    'unit':product.stock_unit,
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
        try:
            for items in order_items:
                OrderItem.objects.create(
                    order = order,
                    product_name=items['product_name'],
                    product_price=items['product_price'],
                    quantity=items['quantity'],
                    subtotal=items['subtotal'],
                    unit=items['unit']
                )
        except Exception as e:
            print("❌ OrderItem creation failed:", e)
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
                subtotal = Decimal(item['quantity']) * Decimal(product_price)
                total += subtotal
                order_items.append({
                    'product': product,
                    'product_name': product.name,
                    'product_price': item['price'],
                    'quantity': item['quantity'],
                    'subtotal': subtotal,
                    'unit':product.stock_unit,
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
                subtotal=items['subtotal'],
                unit=items['unit']
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
            pdf_file = download_file(response[0],response[1])
            return pdf_file
        except:
            messages.error(request,'An error occurs while generating the PDF.')
            return redirect(f'/invoice/{pk}')