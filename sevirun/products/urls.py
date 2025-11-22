from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'products'),
    path('categories/', views.categories, name = 'categories'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('edit/<int:product_id>', views.edit_product, name="edit_product"),
    path('create', views.create_product, name="create_product"),
    path('delete/<int:product_id>', views.delete_product, name="delete_product"),
    path('catalog_management', views.catalog_management, name="catalog_management"),
    path('create_brand', views.create_brand, name="create_brand"),
    path('create_model', views.create_model, name="create_model"),
    path('create_type', views.create_type, name="create_type"),
    path('create_material', views.create_material, name="create_material"),
    path('create_size', views.create_size, name="create_size"),
    path('create_colour', views.create_colour, name="create_colour"),
    path('delete_brand/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('delete_model/<int:model_id>/', views.delete_model, name='delete_model'),
    path('delete_type/<int:type_id>/', views.delete_type, name='delete_type'),
    path('delete_material/<int:material_id>/', views.delete_material, name='delete_material'),
    path('delete_size/<int:size_id>/', views.delete_size, name='delete_size'),
    path('delete_colour/<int:colour_id>/', views.delete_colour, name='delete_colour')
]