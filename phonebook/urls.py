from django.urls import path
from phonebook.views import PhoneBook,EditContactDetails,DeleteContact

urlpatterns = [
    path('contacts/',PhoneBook.as_view(),name='phonebook'),
    path('contact/<str:pk>',EditContactDetails.as_view(),name='addcontact'),
    path('contact/delete/<str:pk>',DeleteContact.as_view(),name='deletecontact'),
]
