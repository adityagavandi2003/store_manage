from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from users.forms import ReportForm
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Report
from django.core.paginator import Paginator
from items.models import Order

# Create your views here.
    
class Notifications(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'notifications.html')

class Profile(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'user/profile.html')

class Setting(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'user/setting.html')

class AddReport(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = ReportForm()
        context = {'form':form}
        return render(request,'report/report.html',context)
    
    def post(self,request,*args, **kwargs):
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.report_by = request.user
            report.save()
            return redirect('/account/my-reports/')

class MyReports(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        reports = Report.objects.filter(report_by=request.user).order_by('-report_at')
        total = reports.count()
        solved = reports.filter(is_solved = True).count()
        unsolved = total - solved
        
        # paginator
        paginator = Paginator(reports, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'reports':page_obj,'solved':solved,'unsolved':unsolved,'total':total}
        return render(request,'report/myreports.html',context)

class ReportView(LoginRequiredMixin,View):
    def get(self,request,pk,*args, **kwargs):
        report = get_object_or_404(Report,report_id=pk)
        context = {'report':report}
        return render(request,'report/viewreport.html',context)

