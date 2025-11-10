from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_customer_orders, name = 'orders'),
    path('sales', views.index_sales, name = 'sales'),
]