from django.urls import path
from . import views

urlpatterns = [
    path('sales', views.index_sales, name = 'sales'),
]