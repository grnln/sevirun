from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'products'),
    path('categories/', views.categories, name = 'categories'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('edit/<int:product_id>', views.edit_product, name="edit_product"),
    path('create', views.create_product, name="create_product"),
    path('delete/<int:product_id>', views.delete_product, name="delete_product"),
]