from django.urls import path
from . import views

urlpatterns = [
    path('pay/method/<int:order_id>/', views.payment_method, name='payment_method'),
    path('pay/start/<int:order_id>/', views.start_payment, name='start_payment'),
    path('pay/ok/<int:order_id>/', views.payment_success, name='redsys_ok'),
    path('pay/ko/<int:order_id>/', views.payment_error, name='redsys_ko'),
    path('pay/notification/<int:order_id>/', views.payment_notification, name='pay_notification'),
]