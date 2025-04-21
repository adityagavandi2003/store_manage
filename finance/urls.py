from django.urls import path
from finance.views import FinanceDashboard,RevenueChart,ProductChart
urlpatterns = [
    path('overview/', FinanceDashboard.as_view(), name='financedashboard'),

    # chart
    path('revenuechart/', RevenueChart.as_view(), name='revenuechart'),
    path('productchart/', ProductChart.as_view(), name='productchart'),
]
