import hashlib
import hmac
from django.test import override_settings
import pytest
pytest_plugins = ['orders.test_fixtures']
from django.urls import reverse
from orders.models import *
from unittest.mock import patch
import cart.views as cart_views
from django.http import HttpResponse
import base64
import json
from decimal import Decimal
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from django.conf import settings


def _make_redsys_config():
    # DES3 key must be 16 or 24 bytes when decoded; use 24 bytes here
    raw_key = get_random_bytes(24)
    key = DES3.adjust_key_parity(raw_key)
    secret_key = base64.b64encode(key).decode()
    return {
        'SECRET_KEY': secret_key,
        'MERCHANT_CODE': 'MERCH123',
        'CURRENCY': '978',
        'TRANSACTION_TYPE': '0',
        'TERMINAL': '1',
        'REDSYS_URL': 'https://example.redsys.test',
    }

def _make_signature_for_payload(order_str, payload_dict, secret_key):
    merchant_parameters = base64.b64encode(json.dumps(payload_dict, separators=(',', ':'), ensure_ascii=False).encode()).decode()
    key = base64.b64decode(secret_key)
    cipher = DES3.new(key, DES3.MODE_CBC, b"\0" * 8)
    order_key = cipher.encrypt(order_str.encode().ljust(16, b"\0"))
    mac = hmac.new(order_key, merchant_parameters.encode(), hashlib.sha256).digest()
    signature = base64.b64encode(mac).decode().replace('+', '-').replace('/', '_')
    return merchant_parameters, signature

# Payment method view tests

@pytest.mark.django_db
def test_payment_method_access_as_unauthenticated(client):
    url = reverse('payment_method', args=[1])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_payment_method_access_as_staff(client, staff_user):
    client.force_login(staff_user)
    url = reverse('payment_method', args=[1])
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_method_access_as_non_owner_client(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('payment_method', args=[2])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_method_access_as_client_owner(client, regular_user, order_list):
    client.force_login(regular_user)
    pending = next((o for o in order_list if o.state == 'PE'), order_list[0])
    pending.client = regular_user
    pending.save()

    url = reverse('payment_method', args=[pending.id])
    response = client.get(url)
    
    assert response.status_code == 200
    assert(response.context['order'].client == regular_user)

@pytest.mark.django_db
def test_payment_method_order_does_not_exist(client, regular_user):
    client.force_login(regular_user)

    url = reverse('payment_method', args=[999])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_method_order_not_pending(client, regular_user, order_and_items_list):
    client.force_login(regular_user)
    order = order_and_items_list
    order.state = 'PR'
    order.save()

    url = reverse('payment_method', args=[order.id])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_method_post_card_selection(client, regular_user, order_and_items_list):
    client.force_login(regular_user)
    order = order_and_items_list
    order.client = regular_user
    order.state = 'PE'
    order.save()

    url = reverse('payment_method', args=[order.id])
    with patch.object(cart_views, 'start_payment', return_value=HttpResponse(status=200)) as mock_start_payment:
        response = client.post(url, data={'method': 'card'})

        assert response.status_code == 200 or response.status_code == 302
        order.refresh_from_db()
        assert order.payment_method == 'CC'
        mock_start_payment.assert_called_once()

@pytest.mark.django_db
def test_payment_method_post_cod_selection(client, regular_user, order_and_items_list):
    client.force_login(regular_user)
    order = order_and_items_list
    order.state = 'PE'
    order.client = regular_user
    order.save()
    url = reverse('payment_method', args=[order.id])

    response = client.post(url, data={'method': 'cod'})

    assert response.status_code == 302
    assert response.url == reverse('payment_ok', args=[order.id])
    order.refresh_from_db()
    assert order.payment_method == 'CA'
    assert order.state == 'PR'

@pytest.mark.django_db
def test_payment_method_invalid_post_selection(client, regular_user, order_and_items_list):
    client.force_login(regular_user)
    order = order_and_items_list
    url = reverse('payment_method', args=[order.id])

    response = client.post(url, data={'method': 'invalid_method'})

    assert response.status_code == 302

# Payment start view tests

@pytest.mark.django_db
def test_start_payment_access_as_unauthenticated(client):
    url = reverse('start_payment', args=[1])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_start_payment_redirects_if_staff(client, staff_user, order_list):
    client.force_login(staff_user)
    url = reverse('start_payment', args=[order_list[0].id])
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_start_payment_access_as_non_owner_client(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('start_payment', args=[order_list[1].id])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_start_payment_access_as_client_owner(client, regular_user, order_list):
    client.force_login(regular_user)
    order = order_list[0]
    order.state = 'PE'
    order.client = regular_user
    order.save()

    url = reverse('start_payment', args=[order.id])
    response = client.get(url)
    
    assert response.status_code == 200

@pytest.mark.django_db
def test_start_payment_order_does_not_exist(client, regular_user):
    client.force_login(regular_user)

    url = reverse('start_payment', args=[999])
    response = client.get(url)
    
    assert response.status_code == 404

@pytest.mark.django_db
def test_start_payment_order_not_pending(client, regular_user, order_and_items_list):
    client.force_login(regular_user)
    order = order_and_items_list
    order.state = 'PR'
    order.save()

    url = reverse('start_payment', args=[order.id])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_start_payment_order_not_pending(client, regular_user, order_and_items_list):
    client.force_login(regular_user)
    order = order_and_items_list
    order.payment_method = 'CA'
    order.save()

    url = reverse('start_payment', args=[order.id])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
@override_settings(REDSYS_CONFIG=_make_redsys_config())
def test_start_payment_renders_with_signature_and_parameters(client, regular_user, order_list):
    client.force_login(regular_user)
    order = order_list[0]
    order.state = 'PE'
    order.payment_method = 'CC'
    order.client = regular_user
    order.save()
    
    url = reverse('start_payment', args=[order.id])
    response = client.get(url)

    assert response.status_code == 200

    ctx = response.context
    assert 'merchant_parameters' in ctx
    assert 'signature' in ctx
    assert ctx.get('signature_version') == 'HMAC_SHA256_V1'
    assert ctx.get('redsys_url') == _make_redsys_config()['REDSYS_URL']

    mp_b64 = ctx['merchant_parameters']
    decoded = base64.b64decode(mp_b64).decode('utf-8')
    data = json.loads(decoded)
    assert data.get('Ds_Merchant_Amount') == str(int(Decimal(order.total_price) * Decimal('100')))
    assert data.get('Ds_Merchant_MerchantCode') == _make_redsys_config()['MERCHANT_CODE']

# Test cases for payment notifications:
@pytest.mark.django_db
@override_settings(REDSYS_CONFIG=_make_redsys_config())
def test_post_valid_signature_updates_order(client, regular_user, order_list):
    order = order_list[0]
    order.state = 'PE'
    order.payment_method = 'CC'
    order.client = regular_user
    order.save()
    secret_key = settings.REDSYS_CONFIG['SECRET_KEY']

    payload = {"Ds_Order": str(order.id), "Ds_Response": "000"}
    merchant_parameters, signature = _make_signature_for_payload(str(order.id), payload, secret_key)

    url = reverse('payment_notification', args=[order.id])
    resp = client.post(url, {
        'Ds_SignatureVersion': 'HMAC_SHA256_V1',
        'Ds_MerchantParameters': merchant_parameters,
        'Ds_Signature': signature,
    })

    assert resp.status_code == 200
    order.refresh_from_db()
    assert order.state == 'PR'

@pytest.mark.django_db
@override_settings(REDSYS_CONFIG=_make_redsys_config())
def test_post_invalid_signature_returns_400(client, regular_user, order_list):
    order = order_list[0]
    order.state = 'PE'
    order.payment_method = 'CC'
    order.client = regular_user
    order.save()

    # Use the secret key from settings to match the view's configuration
    secret_key = settings.REDSYS_CONFIG['SECRET_KEY']

    payload = {"Ds_Order": str(order.id), "Ds_Response": "000"}
    merchant_parameters, signature = _make_signature_for_payload(str(order.id), payload, secret_key)

    bad_signature = signature[:-1] + ('A' if signature[-1] != 'A' else 'B')

    url = reverse('payment_notification', args=[order.id])
    resp = client.post(url, {
        'Ds_SignatureVersion': 'HMAC_SHA256_V1',
        'Ds_MerchantParameters': merchant_parameters,
        'Ds_Signature': bad_signature,
    })

    assert resp.status_code == 400
    order.refresh_from_db()
    assert order.state == 'PE'

@pytest.mark.django_db
def test_missing_params_returns_400(client, regular_user, order_list):
    order = order_list[0]
    order.state = 'PE'
    order.payment_method = 'CC'
    order.client = regular_user
    order.save()

    url = reverse('payment_notification', args=[order.id])
    resp = client.post(url, {})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_get_not_allowed(client, regular_user, order_list):
    order = order_list[0]
    order.state = 'PE'
    order.payment_method = 'CC'
    order.client = regular_user
    order.save()

    url = reverse('payment_notification', args=[order.id])
    resp = client.get(url)
    assert resp.status_code == 400



# Test cases for payment success view:
@pytest.mark.django_db
def test_payment_success_access_as_unauthenticated(client):
    url = reverse('payment_ok', args=[1])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_payment_success_access_as_non_owner_client(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('payment_ok', args=[2])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_success_access_as_staff(client, staff_user, order_list):
    client.force_login(staff_user)

    url = reverse('payment_ok', args=[2])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_success_access_as_client_owner(client, regular_user, order_list):
    client.force_login(regular_user)
    order = order_list[0]
    order.client = regular_user
    order.save()

    url = reverse('payment_ok', args=[order.id])
    response = client.get(url)
    
    assert response.status_code == 200
    assert(response.context['order'].client == regular_user)

@pytest.mark.django_db
def test_payment_success_order_does_not_exist(client, regular_user):
    client.force_login(regular_user)

    url = reverse('payment_ok', args=[999])
    response = client.get(url)
    
    assert response.status_code == 404

# Test cases for payment error view:
@pytest.mark.django_db
def test_payment_error_access_as_unauthenticated(client):
    url = reverse('payment_ko', args=[1])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_payment_error_access_as_non_owner_client(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('payment_ko', args=[2])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_error_access_as_staff(client, staff_user, order_list):
    client.force_login(staff_user)

    url = reverse('payment_ko', args=[2])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('home')