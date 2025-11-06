from django.urls import path

from accounts.views import login_view, logout

urlpatterns = [
    path('login/',login_view, name='login'),
    path('logout/',logout, name='logout'),
]