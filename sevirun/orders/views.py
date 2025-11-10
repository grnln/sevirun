from django.shortcuts import render
from .models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# Create your views here.

@staff_member_required
def index_sales(request):
    sales = Order.objects.filter(state="DE")
    return render(request, 'sales_list.html', { "sales" : sales })

@login_required
def index_customer_orders(request):
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Acceso restringido a clientes.")
    orders = Order.objects.filter(client=request.user)
    return render(request, 'orders_list.html', { "orders" : orders })
