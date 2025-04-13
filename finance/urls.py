from django.urls import path
from finance.views import FinanceDashboard

urlpatterns = [
    path('', FinanceDashboard.as_view(), name='financedashboard'),
]
