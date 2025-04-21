from django.urls import path
from khatabook.views import KhataBook,KhataView

urlpatterns = [
    path('',KhataBook.as_view(),name='khatabook'),
    path('records/<str:pk>',KhataView.as_view(),name='records'),
]
