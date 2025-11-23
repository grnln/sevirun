from django.shortcuts import redirect, render
from .models import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

@staff_member_required(login_url='login')
def index_sales(request):
    sales = Order.objects.filter(state="DE").order_by('-created_at')
    return render(request, 'orders/sales_list.html', { "sales" : sales })

@login_required(login_url='login')
def index_customer_orders(request):
    prev_page = request.GET.get('from', '/')

    if request.user.is_staff or request.user.is_superuser:
        orders = Order.objects.all().order_by('-created_at')

        if request.method == 'POST':
            for order in orders:
                state = request.POST.get(f'order-{order.pk}-state', None)

                if state != None:
                    order.state = state.strip()
                    order.save()
    else:
        orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'orders/orders_list.html', { "orders" : orders, "states": OrderState.choices, 'from': prev_page })

@login_required(login_url='login')
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "El pedido al que intenta acceder no existe.")
        return redirect('orders')

    if not (request.user.is_staff or request.user.is_superuser) and not (order.client == request.user):
        messages.error(request, "El pedido al que intenta acceder no es suyo.")
        return redirect('orders')

    if request.method == 'POST' and (request.user.is_staff or request.user.is_superuser):
        state = request.POST.get(f'order-{order.pk}-state', None)

        if state != None:
            order.state = state.strip()
            order.save()
            
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/order_detail.html', { "order": order, "order_items": order_items, "states": OrderState.choices })

def order_tracking(request, tracking_number):
    try:
        order = Order.objects.get(tracking_number=tracking_number)
    except Order.DoesNotExist:
        messages.error(request, "El pedido al que intenta acceder no existe.")
        return redirect('home')
            
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/order_detail.html', { "order": order, "order_items": order_items, "states": OrderState.choices, 'is_tracking': True })

@staff_member_required(login_url='login')
def delivery_cost(request):
    if not request.user.is_staff:
        return redirect('home')
    
    delivery_cost = DeliveryCost.objects.first()
    if request.method == 'POST':
        try:
            fields = {
                'delivery_cost': request.POST.get('delivery_cost'),
            }
            
            for field, value in fields.items():
                if value:
                    setattr(delivery_cost, field, value)
            
            delivery_cost.save()
            messages.success(request, f'Gastos de envío editados correctamente.')
            return redirect('home')
        
        except Exception as e:
            messages.error(request, f'Error al editar gastos de envío: {str(e)}')
            
    context = {
        'delivery_cost': delivery_cost.delivery_cost
    }
    return render(request, 'orders/delivery_cost.html', context)
