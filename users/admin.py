from django.contrib import admin
from users.models import Report,Notification

# Register your models here.

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_id",'type','report_by', 'subject','is_solved','report_at')

@admin.register(Notification)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id",'shop','notification_type', 'message','created_at')