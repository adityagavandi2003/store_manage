from django.urls import path
from users.views import Notifications,Profile,AddReport,Setting,MyReports,ReportView,PrivacyPolicyView,ReadBy

urlpatterns = [
    path('',Profile.as_view(),name='profile'),
    path('notifications/',Notifications.as_view(),name='notifications'),
    path('notification/seen/<int:id>',ReadBy.as_view(),name='close_notificatons'),
    path('report/',AddReport.as_view(),name='report'),
    path('setting/',Setting.as_view(),name='setting'),
    path('my-reports/',MyReports.as_view(),name='my_reports'),
    path('report/view/<str:pk>/',ReportView.as_view(),name='view_report'),

    path('privacypolicy/',PrivacyPolicyView.as_view(),name='privacy_policy')
]
