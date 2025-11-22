import re

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect,  get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order, OrderItem, OrderType
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings

import base64
import hmac
import hashlib
import json
from django.shortcuts import render
from Crypto.Cipher import DES3
import time
import random
from decimal import Decimal
from .models import *
from products.models import ProductStock
from django.http import JsonResponse
import uuid
from django.utils import timezone
from emails.emailService import send_order_confirmation_email

# Cart views

def order_info(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    session_ok = order.session_id == request.session.get('cart_session_id')
    user_ok = request.user.is_authenticated and order.client == request.user
    if not (session_ok or user_ok):
            messages.error(request, "El pedido al que intenta acceder no es suyo.")
            return redirect('home')

    if request.method == "POST":
        method = request.POST.get("delivery_method")
        address = request.POST.get("shipping_address").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        if phone_number == "" or email == "":
            messages.error(request, "Debe completar todos los campos.")
            return render(request, 'cart/order_info.html', {"order": order})
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "El formato del email no es válido.")
            return render(request, 'cart/order_info.html', {"order": order})
        phone_pattern = re.compile(r'^\+?[\d\s\-]{9,15}$')
        if not phone_pattern.match(phone_number):
            messages.error(request, "El formato del teléfono no es válido.")
            return render(request, 'cart/order_info.html', {"order": order})
        if method == "home" and address == "":
            messages.error(request, "Debe completar todos los campos.")
            return render(request, 'cart/order_info.html', {"order": order})
        if method == "home":
            order.type = OrderType.HOME_DELIVERY
            order.shipping_address = address
            order.delivery_cost = 5.00
        else:
            order.type = OrderType.SHOP
            order.shipping_address = "En tienda"
        order.phone_number = phone_number
        order.client_email = email
        order.save()
        return redirect('payment_method', order_id=order.pk)

    return render(request, 'cart/order_info.html', {"order": order})


def check_items_stock(cart):
    cart.refresh_from_db()
    items = cart.items.all()
    for item in items:
        stock = ProductStock.objects.filter(product=item.product, size=item.size, colour=item.colour)[0].stock
        if item.quantity > stock:
            item.quantity = stock
            item.save()
    cart.refresh_from_db()
    return cart

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(client=request.user)
    else:
        if 'cart_session_id' not in request.session:
            request.session['cart_session_id'] = str(uuid.uuid4())
        
        session_id = request.session.get('cart_session_id')
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    cart = check_items_stock(cart)
    return cart

def get_user_cart(request):
    try: 
        if request.user.is_authenticated:
            return Cart.objects.get(client=request.user)
        else:
            if 'cart_session_id' in request.session:
                return Cart.objects.get(session_id=request.session['cart_session_id'])
    except:
        return None
    return None

def cart(request):
    cart = get_or_create_cart(request)
    return render(request, "cart/view_cart.html", { 'cart': cart })

def add_product_to_cart(request, product_id, colour_id, size_id):
    cart = get_or_create_cart(request)

    product = get_object_or_404(Product, id=product_id)
    colour = get_object_or_404(ProductColour, id=colour_id)
    size = get_object_or_404(ProductSize, id=size_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        colour=colour,
        size=size,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart') 

def update_quantity_ajax(request, item_id, action):
    cart = get_user_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if action == "increase":
        item.quantity += 1

    elif action == "decrease":
        if item.quantity > 1:
            item.quantity -= 1
        
    elif action == "delete":
        cart = item.cart
        item.delete()

        return JsonResponse({
            "deleted": True,
            "subtotal": float(cart.temp_subtotal),
        })

    item.save()
    cart.refresh_from_db()
    cart = check_items_stock(cart)
    item.refresh_from_db()

    item_total = float(item.temp_price)

    cart_total = float(item.cart.temp_subtotal)

    return JsonResponse({
        "deleted": False,
        "quantity": item.quantity,
        "item_total": item_total,
        "subtotal": cart_total,
    })

def create_order_from_cart(request):
    cart = get_user_cart(request)
    cart_items = cart.items.all()

    if len(cart_items) == 0:
        messages.error(request, "El carrito está vacío.")
        return redirect('cart')
    
    cart_client = cart.client if cart.client else None
    cart_session_id = cart.session_id if cart.session_id else None

    order = Order.objects.create(client=cart_client, session_id=cart_session_id, created_at=timezone.now(), state="PE", delivery_cost=0.0, discount_percentage=0.0)
    for item in cart_items:
        price = item.product.price_on_sale if item.product.price_on_sale else item.product.price
        OrderItem.objects.create(order=order, product=item.product, size=item.size, colour=item.colour, quantity=item.quantity, unit_price=price)
    cart.delete()

    return redirect('order_info', order_id=order.pk)

# Payment views
# Example credit card for testing: 4548812049400004

def start_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    session_ok = order.session_id == request.session.get('cart_session_id')
    user_ok = request.user.is_authenticated and order.client == request.user
    if not (session_ok or user_ok):
        messages.error(request, "El pedido al que intenta pagar no es suyo.")
        return redirect('home')
    
    if order.state != 'PE':
        messages.info(request, "El pedido ya ha sido pagado o no está pendiente de pago.")
        return redirect('home')
    
    if order.payment_method != 'CC':
        messages.error(request, "El método de pago seleccionado no es válido para este pedido.")
        return redirect('home')
    
    config = getattr(settings, 'REDSYS_CONFIG', None) or {}
    secret_key = config.get('SECRET_KEY')
    merchant_code = config.get('MERCHANT_CODE')
    currency = config.get('CURRENCY')
    transaction_type = config.get('TRANSACTION_TYPE')
    terminal = config.get('TERMINAL')
    redsys_url = config.get('REDSYS_URL')

    data = {
        "Ds_Merchant_Amount": "",
        "Ds_Merchant_Order": "",
        "Ds_Merchant_MerchantCode": merchant_code,
        "Ds_Merchant_Currency": currency,
        "Ds_Merchant_TransactionType": transaction_type,
        "Ds_Merchant_Terminal": terminal,
        "Ds_Merchant_MerchantURL": request.build_absolute_uri(reverse('payment_notification', args=[order_id])),
        "Ds_Merchant_UrlOK": request.build_absolute_uri(reverse('payment_ok', args=[order_id])),
        "Ds_Merchant_UrlKO": request.build_absolute_uri(reverse('payment_ko', args=[order_id])),
    }
    
    # Generar un número de pedido único para Redsys - Se podría usar otro método
    epoch_sec = str(int(time.time()))[-10:]
    rand2 = str(random.randint(0, 99)).zfill(2)
    unique_order = (epoch_sec + rand2)[:12]
    data["Ds_Merchant_Order"] = unique_order

    amount = Decimal(getattr(order, 'total_price', getattr(order, 'total', 0)))
    amount_cents = str(int(amount * Decimal('100')))
    data["Ds_Merchant_Amount"] = amount_cents

    # Convertir dict → JSON → base64
    json_data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    merchant_parameters = base64.b64encode(json_data.encode()).decode()

    # Crear la firma según Redsys (3DES + HMAC SHA256)
    order = data["Ds_Merchant_Order"].encode()
    key = base64.b64decode(secret_key)

    cipher = DES3.new(key, DES3.MODE_CBC, b"\0" * 8)
    order_key = cipher.encrypt(order.ljust(16, b"\0"))

    mac = hmac.new(order_key, merchant_parameters.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(mac).decode().replace('+', '-').replace('/', '_')

    return render(request, "cart/start_payment.html", {
        "signature_version": "HMAC_SHA256_V1",
        "merchant_parameters": merchant_parameters,
        "signature": signature,
        "redsys_url": redsys_url,
    })

@csrf_exempt
def payment_notification(request, order_id):
    
    if request.method != "POST":
        return HttpResponse("Invalid", status=400)

    ds_signature_version = request.POST.get("Ds_SignatureVersion")
    ds_merchant_parameters = request.POST.get("Ds_MerchantParameters")
    ds_signature = request.POST.get("Ds_Signature")

    if not all([ds_signature_version, ds_merchant_parameters, ds_signature]):
        return HttpResponse("Faltan datos", status=400)


    config = getattr(settings, 'REDSYS_CONFIG', None) or {}
    secret_key = config.get('SECRET_KEY')

    # Decodificar parámetros y generar firma local
    decoded = base64.b64decode(ds_merchant_parameters).decode("utf-8")
    data = json.loads(decoded)

    order_str = data.get("Ds_Order")
    if not order_str:
        return HttpResponse("Sin número de pedido", status=400)

    key = base64.b64decode(secret_key)
    cipher = DES3.new(key, DES3.MODE_CBC, b"\0" * 8)
    order_key = cipher.encrypt(order_str.encode().ljust(16, b"\0"))
    mac = hmac.new(order_key, ds_merchant_parameters.encode(), hashlib.sha256).digest()
    local_signature = base64.b64encode(mac).decode().replace("+", "-").replace("/", "_")

    # Comparar firmas
    if local_signature == ds_signature:
        response_code = data.get('Ds_Response', '')
        response_int = int(response_code) if response_code.isdigit() else 9999
        if 0 <= response_int < 100:
            # Actualizar el pedido
            try:
                order_obj = Order.objects.get(id=int(order_id))
                if order_obj.state == 'PE':
                    order_obj.state = 'PR'
                    for item in order_obj.items.all():
                        stock_obj = ProductStock.objects.get(
                            product=item.product,
                            size=item.size,
                            colour=item.colour,
                        )
                        if stock_obj.stock >= item.quantity:
                            stock_obj.stock -= item.quantity
                        else:
                            stock_obj.stock = 0
                        stock_obj.save()
                    order_obj.save()
                    
            except Order.DoesNotExist:
                pass
        
        return HttpResponse("OK")
    else:
        return HttpResponse("Firma inválida", status=400)

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    session_ok = order.session_id == request.session.get('cart_session_id')
    user_ok = request.user.is_authenticated and order.client == request.user
    if not (session_ok or user_ok):
        messages.error(request, "El pedido al que intenta pagar no es suyo.")
        return redirect('home')
    if not order.tracking_number:
        order.tracking_number = str(uuid.uuid4())
        order.save()
    tracking_url = request.build_absolute_uri(
        reverse('order_tracking', kwargs={'tracking_number': order.tracking_number})
    )
    if request.user.is_authenticated:
        recipient = request.user.email
    else:
        recipient = order.client_email
    send_order_confirmation_email(order, tracking_url, recipient)
    return render(request, 'cart/payment_success.html', {"order": order})

def payment_error(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    session_ok = order.session_id == request.session.get('cart_session_id')
    user_ok = request.user.is_authenticated and order.client == request.user
    if not (session_ok or user_ok):
        messages.error(request, "El pedido al que intenta pagar no es suyo.")
        return redirect('home')
    return render(request, 'cart/payment_error.html', {"order": order})

@require_http_methods(['GET', 'POST'])
def payment_method(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "El pedido al que intenta acceder no existe.")
        return redirect('home')

    if request.user.is_staff:
        messages.error(request, "Esta vista es sólo para clientes.")
        return redirect('home')

    session_ok = order.session_id == request.session.get('cart_session_id')
    user_ok = request.user.is_authenticated and order.client == request.user
    if not (session_ok or user_ok):
        messages.error(request, "El pedido al que intenta pagar no es suyo.")
        return redirect('home')
    
    if order.state != 'PE':
        messages.info(request, "El pedido ya ha sido pagado o no está pendiente de pago.")
        return redirect('home')

    if order.client_email is None or order.phone_number is None or (order.type == OrderType.HOME_DELIVERY and order.shipping_address is None):
        messages.error(request, "Debe completar la información del pedido antes de seleccionar el método de pago.")
        return redirect('order_info', order_id=order.pk)

    # Verify stock
    if request.method == 'POST':
        for item in order.items.all():
            try:
                stock = ProductStock.objects.get(
                    product=item.product,
                    size=item.size,
                    colour=item.colour,
                )
            except ProductStock.DoesNotExist:
                stock = None

            if stock is None or stock.stock < item.quantity:
                messages.error(request, f"No hay suficiente stock para el producto {item.product.name} en la talla {item.size.name} y color {item.colour.name}.")
                return redirect('cart')

    if request.method == 'POST' and request.POST.get('method') == 'card':
        order.payment_method = 'CC'
        order.save()
        return start_payment(request, order_id)
    
    if request.method == 'POST' and request.POST.get('method') == 'cod':
        order.payment_method = 'CA'
        order.state = 'PR'
        for item in order.items.all():
            stock = ProductStock.objects.get(
                product=item.product,
                size=item.size,
                colour=item.colour,
            )
            if stock.stock >= item.quantity:
                stock.stock -= item.quantity
            else:
                stock.stock = 0
            stock.save()
        order.save()
        return redirect('payment_ok', order_id=order_id)

    return render(request, 'cart/payment_method.html', {"order": order})
