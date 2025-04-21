from django.contrib import admin
from phonebook.models import AddContact

# Register your models here.

@admin.register(AddContact)
class AddContactAdmin(admin.ModelAdmin):
    list_display = [ 'id','name','phone_number','created_at']
    readonly_fields = ['created_at']