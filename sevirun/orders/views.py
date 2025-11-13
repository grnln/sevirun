from django.shortcuts import redirect, render
from .models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

@staff_member_required(login_url='login')
def index_sales(request):
    sales = Order.objects.filter(state="DE")
    return render(request, 'orders/sales_list.html', { "sales" : sales })

@login_required(login_url='login')
def index_customer_orders(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('sales')
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'orders/orders_list.html', { "orders" : orders })

@login_required(login_url='login')
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "El pedido al que intenta acceder no existe.")
        if request.user.is_staff:
            return redirect('sales')
        return redirect('orders')

    if request.user.is_staff:
        messages.error(request, "Esta vista es sólo para clientes.")
        return redirect('sales')
    
    if not (order.client == request.user):
        messages.error(request, "El pedido al que intenta acceder no es suyo.")
        return redirect('orders')

    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/order_detail.html', { "order": order, "order_items": order_items })
