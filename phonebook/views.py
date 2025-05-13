from sqlite3 import IntegrityError
from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from phonebook.models import AddContact
from phonebook.forms import ContactAddForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
# Create your views here.
class PhoneBook(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = ContactAddForm()
        contacts = AddContact.objects.filter(shop=request.user).order_by('name')
        
        context = {
            'form':form,
            'contacts':contacts
        }
        return render(request,'contacts.html',context)
    
    def post(self,request,*args, **kwargs): 
        try:
            form = ContactAddForm(request.POST)
            if form.is_valid():
                contact = form.save(commit=False)
                contact.shop = request.user
                contact.save()
                messages.success(request,'Contact add successfully')
                return redirect('/phone-book/contacts/')
            else:
                messages.error(request, "This phone number is already in your contacts.")
                return redirect('/phone-book/contacts/')
        except Exception as e:
            messages.error(request, "This phone number is already in your contacts.")
            print(f'error: {e}')
            return redirect('/phone-book/contacts/')
        
    
class EditContactDetails(LoginRequiredMixin,View):
    def get(self,request,pk,*args, **kwargs):
        contact = get_object_or_404(AddContact,id=pk)

        contacts = AddContact.objects.filter(shop=request.user).order_by('name')
        form = ContactAddForm(instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request,'Contact updated')
            return render('/phone-book/contacts/')
        
        context = {
            'forms':form,
            'contact':contact,
            'contacts':contacts,
        }
        return render(request,'contacts.html',context)
    
    def post(self,request,pk,*args, **kwargs):
        contact = get_object_or_404(AddContact,id=pk)
        form = ContactAddForm(request.POST,instance=contact)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.shop = request.user
            contact.save()
            messages.success(request,'Contact add successfully')
            return redirect('/phone-book/contacts/')
        else:
            messages.error(request, "This phone number is already in your contacts.")
            return redirect('/phone-book/contacts/')
        

class DeleteContact(LoginRequiredMixin,View):
    def get(self,request,pk):
        contact = get_object_or_404(AddContact,id=pk)
        if contact:
            contact.delete()
            messages.success(request,'Contact deleted')
            return redirect('/phone-book/contacts/')
        else:
            messages.error(request,'Contact already deleted')
            return redirect('/phone-book/contacts/')
