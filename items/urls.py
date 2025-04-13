from django.urls import path
from items.views import Home, Dashboard, Add_Product, Edit_Product, Delete_Product, View_Product, SalesOverview,AddToCart,Checkout,DeleteCart,ClearCart,ItemsOrder
urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('products/', View_Product.as_view(), name='viewproduct'),
    path('salesoverview/', SalesOverview.as_view(), name='salesoverview'),
    path('product/add/', Add_Product.as_view(), name='addproduct'),
    path('product/edit/<str:pk>', Edit_Product.as_view(), name='editproduct'),
    path('product/delete/<str:pk>', Delete_Product.as_view(), name='deleteproduct'),

    # cart
    path('add-to-cart/<str:pk>/', AddToCart.as_view(), name='add_to_cart'),
    path('deletecartitem/<str:pk>/', DeleteCart.as_view(), name='deleteitemcart'),
    path('clearcart/', ClearCart.as_view(), name='clearcart'),
    path('checkout/', Checkout.as_view(), name='checkout'),

    # order
    path('order/',ItemsOrder.as_view(),name='orders'),
]
