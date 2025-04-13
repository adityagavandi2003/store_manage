from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

class FinanceDashboard(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'financedashboard.html')