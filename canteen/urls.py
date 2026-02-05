from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('add-to-cart/<int:stock_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
path('place-order/', views.place_order, name='place_order'),

    path('ajax/increase/<int:stock_id>/', views.ajax_increase_cart, name='ajax_increase_cart'),
    path('ajax/decrease/<int:stock_id>/', views.ajax_decrease_cart, name='ajax_decrease_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('payment/', views.payment_page, name='payment'),
path('payment/success/', views.payment_success, name='payment_success'),
path('download-receipt/<str:order_id>/', views.download_receipt, name='download_receipt'),
path('profile/', views.student_profile, name='student_profile'),

]


