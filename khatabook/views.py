from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from items.models import Order, OrderItem, Product
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class KhataBook(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        khata_summary = Order.objects.filter(
            shop=request.user,is_paid=False,payment_mode='KhataBook'
            ).values('customer').annotate(total_due=Sum('total_amount'))
        total_due = khata_summary.aggregate(due_total=Sum('total_due'))
        context = {
            'khatas':khata_summary,
            'Due_total':total_due,
        }
        return render(request,'dairy.html',context)

class KhataView(LoginRequiredMixin,View):
    def get(self,request,pk,*args, **kwargs):
        customer_khata = Order.objects.filter(
            shop=request.user,
            is_paid=False,
            payment_mode='KhataBook',
            customer=pk 
        )
        total_due = customer_khata.values('customer','customer_phone').annotate(total_due=Sum('total_amount')).order_by('customer').first()
        order_items = []
        for order in customer_khata:
            items = OrderItem.objects.filter(order=order)
            for item in items:
                order_items.append({
                    'product_name':item.product_name,
                    'product_price':item.product_price,
                    'product_quantity':item.quantity,
                    'product_subtotal':item.subtotal
                })
        context = {
            'khata':total_due,
            'orders':order_items,
        }
        return render(request,'khataaccount.html',context)
    