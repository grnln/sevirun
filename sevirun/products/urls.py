from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'products'),
    path('categories/', views.categories, name = 'categories'),
    path('<int:product_id>/', views.product_detail, name='product_detail')
]