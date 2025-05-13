from django.urls import path
from items.views import Home, Dashboard, Add_Product, Edit_Product, Delete_Product, View_Product, SalesOverview,AddToCart,Checkout,DeleteCart,ClearCart,OnlinePaymentView,OfflinePaymentView,PaymentCallbackView,OrderSucessView,OrderFailedView,InvoiceView,ProductView,SearchView


urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('salesoverview/', SalesOverview.as_view(), name='salesoverview'),

    # product operations
    path('products/', View_Product.as_view(), name='viewproduct'),  # all products
    path('product/view/<str:pk>',ProductView.as_view(),name='productview'), # view perticular product
    path('product/add/', Add_Product.as_view(), name='addproduct'), # add product 
    path('product/edit/<str:pk>', Edit_Product.as_view(), name='editproduct'),  # edit product
    path('product/delete/<str:pk>', Delete_Product.as_view(), name='deleteproduct'),  # delete product

    # cart operations
    path('add-to-cart/<str:pk>/', AddToCart.as_view(), name='add_to_cart'),
    path('deletecartitem/<str:pk>/', DeleteCart.as_view(), name='deleteitemcart'),
    path('clearcart/', ClearCart.as_view(), name='clearcart'),
    path('checkout/', Checkout.as_view(), name='checkout'),

    # order operations
    path('payment/',OfflinePaymentView.as_view(),name='payment'), #  offline and khatabook
    path('payment/online/',OnlinePaymentView.as_view(),name='onlinepayment'),
    path('payment-verify/',PaymentCallbackView.as_view(),name='payment_verify'),

    # order operations
    path('success/',OrderSucessView.as_view(),name='order_success'),
    path('failed/',OrderFailedView.as_view(),name='order_failed'),

    # invoice operations
    path('invoice/<str:pk>',InvoiceView.as_view(),name='invoice'),

    # search
    path('search/',SearchView.as_view(),name='search')
]
