from django.contrib import messages
from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
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

# Cart views

@login_required(login_url='login')
def cart(request):
    currentUser = request.user
    cart = list(Cart.objects.filter(client=currentUser))
    if len(cart) == 0:
        cart = Cart.objects.create(cclient=currentUser)
    return render(request, "cart/view_cart.html", { 'cart': Cart.objects.filter(client=currentUser)[0] })

# Payment views
# Example credit card for testing: 4548812049400004

@login_required(login_url='/login/')
def start_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.client != request.user:
        messages.error(request, "El pedido al que intenta pagar no es suyo.")
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
                    order_obj.save()
                    
            except Order.DoesNotExist:
                pass
        
        return HttpResponse("OK")
    else:
        return HttpResponse("Firma inválida", status=400)

@login_required(login_url='/login/')
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.client != request.user:
        messages.error(request, "El pedido al que intenta ver no es suyo.")
        return redirect('home')
    return render(request, 'cart/payment_success.html', {"order": order})

@login_required(login_url='/login/')
def payment_error(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.client != request.user:
        messages.error(request, "El pedido al que intenta ver no es suyo.")
        return redirect('home')
    return render(request, 'cart/payment_error.html', {"order": order})

@login_required(login_url='/login/')
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
    
    if not (order.client == request.user):
        messages.error(request, "El pedido al que intenta pagar no es suyo.")
        return redirect('home')
    
    if order.state != 'PE':
        messages.info(request, "El pedido ya ha sido pagado o no está pendiente de pago.")
        return redirect('home')
    
    if request.method == 'POST' and request.POST.get('method') == 'card':
        order.payment_method = 'CC'
        order.save()
        return start_payment(request, order_id)
    
    if request.method == 'POST' and request.POST.get('method') == 'cod':
        order.payment_method = 'CA'
        order.state = 'PR'
        order.save()
        return redirect('payment_ok', order_id=order_id)

    return render(request, 'cart/payment_method.html', {"order": order})
