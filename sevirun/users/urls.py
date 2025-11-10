from django.urls import path
from . import views

urlpatterns = [
    path('admin/all', views.admin_users_view, name = 'admin_users'),
    path('admin/create/', views.admin_create_user, name='admin_create_user'),
    path('admin/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
]