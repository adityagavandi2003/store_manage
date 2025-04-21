from django.shortcuts import render,redirect
from django.views import View

class LandPageView(View):
    def get(self,request,*args, **kwargs):
        return render(request,'landpage.html')