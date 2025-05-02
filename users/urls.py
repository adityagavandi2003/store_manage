from django.urls import path
from users.views import Notifications,Profile,AddReport,Setting,MyReports,ReportView,ChangeUsernameView,DeleteAccountView,PrivacyPolicyView

urlpatterns = [
    path('',Profile.as_view(),name='profile'),
    path('notifications/',Notifications.as_view(),name='notifications'),
    path('report/',AddReport.as_view(),name='report'),
    path('setting/',Setting.as_view(),name='setting'),
    path('my-reports/',MyReports.as_view(),name='my_reports'),
    path('report/view/<str:pk>/',ReportView.as_view(),name='view_report'),

    path('change/username/',ChangeUsernameView.as_view(),name='change_username'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    path('privacypolicy/',PrivacyPolicyView.as_view(),name='privacy_policy')
]
