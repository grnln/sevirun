from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path("update-ajax/<int:item_id>/<str:action>/", 
        views.update_quantity_ajax, 
        name="update_quantity_ajax"),
    path('add/<int:product_id>/<int:colour_id>/<int:size_id>/<int:quantity>', 
        views.add_product_to_cart, 
        name='add_to_cart'),
    path('create-order', views.create_order_from_cart, name='create_order_from_cart'),
    path('pay/method/<int:order_id>/', views.payment_method, name='payment_method'),
    path('pay/start/<int:order_id>/', views.start_payment, name='start_payment'),
    path('pay/ok/<int:order_id>/', views.payment_success, name='payment_ok'),
    path('pay/ko/<int:order_id>/', views.payment_error, name='payment_ko'),
    path('pay/notification/<int:order_id>/', views.payment_notification, name='payment_notification'),
    path('info/<int:order_id>/', views.order_info, name='order_info'),
]