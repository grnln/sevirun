from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path("update-ajax/<int:item_id>/<str:action>/", 
        views.update_quantity_ajax, 
        name="update_quantity_ajax"),
    path('pay/method/<int:order_id>/', views.payment_method, name='payment_method'),
    path('pay/start/<int:order_id>/', views.start_payment, name='start_payment'),
    path('pay/ok/<int:order_id>/', views.payment_success, name='payment_ok'),
    path('pay/ko/<int:order_id>/', views.payment_error, name='payment_ko'),
    path('pay/notification/<int:order_id>/', views.payment_notification, name='payment_notification'),
]