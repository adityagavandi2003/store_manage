from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from users.forms import ReportForm
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Report,Notification
from django.core.paginator import Paginator
from allauth.account.forms import AddEmailForm
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email
from django.contrib import messages
from allauth.account.forms import ChangePasswordForm
# Create your views here.

class LandPageView(View):
    def get(self,request,*args, **kwargs):
        return render(request,'landpage.html')

class Notifications(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'notifications.html')
    
class ReadBy(LoginRequiredMixin,View):
    def get(self,request,id,*args, **kwargs):
        notif = get_object_or_404(Notification, id=id)
        notif.is_read_by.add(request.user)
        return redirect(request.GET.get("next", "dashboard"))

class Profile(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        user = request.user
        emailaddresses = EmailAddress.objects.filter(user=user)
        initial_email = user_email(user)
        emailaddress_radios = [
            {
                "id": f"email_radio_{idx}",
                "emailaddress": ea,
                "checked": ea.email == initial_email,
            }
            for idx, ea in enumerate(emailaddresses)
        ]
        form = AddEmailForm(user=user)
        can_add_email = True 
        changepassowrd = ChangePasswordForm(user=request.user)
        context = {
            "emailaddresses": emailaddresses,
            "emailaddress_radios": emailaddress_radios,
            "form": form,
            'changepassword':changepassowrd,
            "can_add_email": can_add_email,
        }
        return render(request,'user/profile.html',context)
    
    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()

            backend = settings.AUTHENTICATION_BACKENDS[1]  # backend authentication import from setting.py
            login(request, request.user, backend=backend)

            messages.success(request, 'Your password has been successfully changed.')
            return redirect('profile') 
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'user/profile.html', {'form': form})


class Setting(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        return render(request,'user/setting.html')
    
    def post(self, request):
        if 'change_store_name' in request.POST:
            store_name = request.POST.get('store_name')
            if store_name:
                request.user.username = store_name
                request.user.save()
                messages.success(request, "Store name updated.")
            else:
                messages.error(request, "Store name cannot be empty.")
        elif 'delete_account' in request.POST:
            try:
                EmailAddress.objects.filter(user=request.user).delete()
                request.user.delete()
                messages.success(request, "Account deleted.")
                return redirect('account_login')
            except Exception as e:
                messages.error(request, f"Error deleting account: {str(e)}")
        return redirect('profile')

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

class PrivacyPolicyView(View):
    def get(self,request,*args, **kwargs):
        return render(request,'user/privacypolicy.html')