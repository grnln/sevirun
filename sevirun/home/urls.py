from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('collections/', views.collections, name='collections'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('accounts/login/', views.login_view, name='login'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]