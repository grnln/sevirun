import hashlib
import hmac

from django.contrib.auth import get_user_model
from django.test import override_settings
pytest_plugins = ['orders.test_fixtures']
from django.urls import reverse
from unittest.mock import patch
import cart.views as cart_views
from django.http import HttpResponse
import base64
import json
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from django.conf import settings
from cart.test_fixtures import *
from users.test_fixtures import *

from unittest.mock import patch

user_data = {
    "email": "newuser@user.com",
    "password": "newuser",
    "name": "new",
    "surname": "user",
    "phone_number": "123456789",
    "address": "Sample address",
    "city": "Sample Town",
    "postal_code": "38678"
}

user2_data = {
    "email": "newuser2@user.com",
    "password": "newuser2",
    "name": "new",
    "surname": "user",
    "phone_number": "123456789",
    "address": "Sample address",
    "city": "Sample Town",
    "postal_code": "38678"
}

not_delivered_order = {
      "created_at": "2025-01-01T00:00:00.000+01:00",
      "state": "PE",
      "delivery_cost": Decimal("5.5"),
      "discount_percentage": Decimal("10.0"),
      "payment_method": "CC",
      "shipping_address": "Fake street, 123, 12345, City, Country",
      "phone_number": "+341234356789"
}

not_delivered_incomplete_order = {
      "created_at": "2025-01-01T00:00:00.000+01:00",
      "state": "PE",
      "delivery_cost": Decimal("5.5"),
      "discount_percentage": Decimal("10.0"),
      "payment_method": "CC",
      "shipping_address": "",
      "phone_number": ""
}

def _make_redsys_config():
    # DES3 key must be 16 or 24 bytes when decoded; use 24 bytes here
    raw_key = get_random_bytes(24)
    key = DES3.adjust_key_parity(raw_key)
    secret_key = base64.b64encode(key).decode()
    return {
        'REDSYS_SECRET_KEY': secret_key,
        'REDSYS_MERCHANT_CODE': 'MERCH123',
        'REDSYS_CURRENCY': '978',
        'REDSYS_TRANSACTION_TYPE': '0',
        'REDSYS_TERMINAL': '1',
        'REDSYS_URL': 'https://example.redsys.test',
        'RESEND_API_KEY': os.environ['RESEND_API_KEY']
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
User = get_user_model()

@pytest.fixture(autouse=True)
def mock_send_email():
    with patch('cart.views.send_order_confirmation_email') as mock:
        yield mock

@pytest.mark.django_db
def test_order_info_access_with_authenticated_user(client, django_user_model):
    user = django_user_model.objects.create_user(**user_data)
    client.force_login(user)

    session = client.session
    session['cart_session_id'] = 'test_session_123'
    session.save()

    order = Order.objects.create(
        client=user,
        session_id='test_session',
        created_at=timezone.now(),
        **{k: v for k, v in not_delivered_order.items() if k not in ('created_at',)}
    )

    response = client.get(reverse('order_info', kwargs={'order_id': order.id}))
    assert response.status_code == 200
    assert response.context['order'] == order
    assert "La tienda no contempla devoluciones online" in response.content.decode('utf-8')
    assert "Fake street, 123, 12345, City, Country" in response.content.decode('utf-8')
    assert "+341234356789" in response.content.decode('utf-8')
    assert "newuser@user.com" in response.content.decode('utf-8')

@pytest.mark.django_db
def test_order_info_access_with_wrong_user(client, django_user_model):
    user = django_user_model.objects.create_user(**user_data)
    other_user = django_user_model.objects.create_user(**user2_data)
    client.force_login(other_user)

    session = client.session
    session['cart_session_id'] = 'test_session_123'
    session.save()

    order = Order.objects.create(
        client=user,
        session_id='test_session',
        created_at=timezone.now(),
        **{k: v for k, v in not_delivered_order.items() if k not in ('created_at',)}
    )

    response = client.get(reverse('order_info', kwargs={'order_id': order.id}), follow=True)
    print(response.content.decode('utf-8'))
    assert response.status_code == 200
    assert 'El pedido al que intenta acceder no es suyo.' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_incomplete_order_info(client, django_user_model):
    user = django_user_model.objects.create_user(**user_data)
    client.force_login(user)

    session = client.session
    session['cart_session_id'] = 'test_session_123'
    session.save()

    order = Order.objects.create(
        client=user,
        session_id='test_session',
        created_at=timezone.now(),
        **{k: v for k, v in not_delivered_incomplete_order.items() if k not in ('created_at',)}
    )

    response = client.get(reverse('payment_method', kwargs={'order_id': order.id}), follow=True)
    assert response.status_code == 200
    assert 'Debe completar la información del pedido antes de seleccionar el método de pago.' in response.content.decode('utf-8')


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

    initial_stock = {}
    for item in order.items.all():
        ps = ProductStock.objects.create(
            product=item.product,
            size=item.size,
            colour=item.colour,
            stock=10
        )
        initial_stock[item.pk] = ps.stock

    url = reverse('payment_method', args=[order.id])
    with patch.object(cart_views, 'start_payment', return_value=HttpResponse(status=200)) as mock_start_payment:
        response = client.post(url, data={'method': 'card'})

        assert response.status_code == 200 or response.status_code == 302
        order.refresh_from_db()
        assert order.payment_method == 'CC'
        mock_start_payment.assert_called_once()

@pytest.mark.django_db
def test_payment_method_post_cod_selection(client, regular_user, order_and_items_list, mock_send_email):
    client.force_login(regular_user)
    order = order_and_items_list
    order.state = 'PE'
    order.client = regular_user
    order.save()
    url = reverse('payment_method', args=[order.id])
    
    initial_stock = {}
    for item in order.items.all():
        ps = ProductStock.objects.create(
            product=item.product,
            size=item.size,
            colour=item.colour,
            stock=10
        )
        initial_stock[item.pk] = ps.stock

    response = client.post(url, data={'method': 'cod'})

    assert response.status_code == 302
    assert response.url == reverse('payment_ok', args=[order.id])
    order.refresh_from_db()
    assert order.payment_method == 'CA'
    assert order.state == 'PR'
    for item in order.items.all():
        ps = ProductStock.objects.get(product=item.product, size=item.size, colour=item.colour)
        assert ps.stock == initial_stock[item.pk] - item.quantity
    mock_send_email.assert_called_once()

@pytest.mark.django_db
def test_payment_method_invalid_post_selection(client, regular_user, order_and_items_list, mock_send_email):
    client.force_login(regular_user)
    order = order_and_items_list
    url = reverse('payment_method', args=[order.id])

    response = client.post(url, data={'method': 'invalid_method'})

    assert response.status_code == 302
    mock_send_email.assert_not_called()

@pytest.mark.django_db
def test_payment_method_insufficient_stock_redirects_to_cart(client, regular_user, order_and_items_list, mock_send_email):
    client.force_login(regular_user)
    order = order_and_items_list
    order.state = 'PE'
    order.client = regular_user
    order.save()

    items = list(order.items.all())
    
    # Item with stock insufficient (quantity in fixture: 2)
    ProductStock.objects.create(
        product=items[0].product,
        size=items[0].size,
        colour=items[0].colour,
        stock=1,
    )
    # Item with sufficient stock
    ProductStock.objects.create(
        product=items[1].product,
        size=items[1].size,
        colour=items[1].colour,
        stock=10,
    )

    url = reverse('payment_method', args=[order.id])
    response = client.post(url, data={'method': 'card'})

    assert response.status_code == 302
    assert response.url == reverse('cart')
    order.refresh_from_db()
    assert order.state == 'PE'
    mock_send_email.assert_not_called()

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
    with patch.dict('os.environ', _make_redsys_config()):
        client.force_login(regular_user)

        url = reverse('start_payment', args=[order_list[1].id])
        response = client.get(url)
    
        assert response.status_code == 302
        assert response.url == reverse('home')

@pytest.mark.django_db
def test_start_payment_access_as_client_owner(client, regular_user, order_list):
    with patch.dict('os.environ', _make_redsys_config()):
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
def test_start_payment_renders_with_signature_and_parameters(client, regular_user, order_list):
    with patch.dict('os.environ', _make_redsys_config()):
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
        assert ctx.get('redsys_url') == os.environ['REDSYS_URL']

        mp_b64 = ctx['merchant_parameters']
        decoded = base64.b64decode(mp_b64).decode('utf-8')
        data = json.loads(decoded)
        assert data.get('Ds_Merchant_Amount') == str(int(Decimal(order.total_price) * Decimal('100')))
        assert data.get('Ds_Merchant_MerchantCode') == os.environ['REDSYS_MERCHANT_CODE']

# Test cases for payment notifications:
@pytest.mark.django_db
def test_payment_notification_post_valid_signature_updates_order(client, regular_user, order_and_items_list):
    with patch.dict('os.environ', _make_redsys_config()):
        order = order_and_items_list
        order.state = 'PE'
        order.payment_method = 'CC'
        order.client = regular_user
        order.save()

        initial_stock = {}
        for item in order.items.all():
            ps = ProductStock.objects.create(
                product=item.product,
                size=item.size,
                colour=item.colour,
                stock=10
            )
            initial_stock[item.pk] = ps.stock

        secret_key = os.environ['REDSYS_SECRET_KEY']

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

        for item in order.items.all():
            ps = ProductStock.objects.get(product=item.product, size=item.size, colour=item.colour)
            assert ps.stock == initial_stock[item.pk] - item.quantity

@pytest.mark.django_db
def test_payment_notification_post_invalid_signature_returns_400(client, regular_user, order_list):
    with patch.dict('os.environ', _make_redsys_config()):
        order = order_list[0]
        order.state = 'PE'
        order.payment_method = 'CC'
        order.client = regular_user
        order.save()

        # Use the secret key from settings to match the view's configuration
        secret_key = os.environ['REDSYS_SECRET_KEY']

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
def test_payment_notification_missing_params_returns_400(client, regular_user, order_list):
    order = order_list[0]
    order.state = 'PE'
    order.payment_method = 'CC'
    order.client = regular_user
    order.save()

    url = reverse('payment_notification', args=[order.id])
    resp = client.post(url, {})
    assert resp.status_code == 400


@pytest.mark.django_db
def test_payment_notification_get_not_allowed(client, regular_user, order_list):
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
    with patch.dict('os.environ', _make_redsys_config()):
        client.force_login(regular_user)

        url = reverse('payment_ok', args=[2])
        response = client.get(url)
    
        assert response.status_code == 302
        assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_success_access_as_staff(client, staff_user, order_list):
    with patch.dict('os.environ', _make_redsys_config()):
        client.force_login(staff_user)

        url = reverse('payment_ok', args=[2])
        response = client.get(url)
    
        assert response.status_code == 302
        assert response.url == reverse('home')

@pytest.mark.django_db
def test_payment_success_access_as_client_owner(client, regular_user, order_list):
    with patch.dict('os.environ', _make_redsys_config()):
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

@pytest.mark.django_db
def test_view_existing_unauth_cart(client, unauth_cart):
    url = reverse('cart')

    previousCartCount = len(Cart.objects.all())

    session = client.session
    session['cart_session_id'] = unauth_cart.session_id
    session.save()
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'Test Product' in response.content
    assert currentCartCount == 1
    assert previousCartCount == currentCartCount

@pytest.mark.django_db
def test_view_existing_auth_cart(client, regular_user, auth_cart):
    client.force_login(regular_user)
    previousCartCount = len(Cart.objects.all())

    url = reverse('cart')
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'Test Product' in response.content
    assert currentCartCount == 1
    assert previousCartCount == currentCartCount

@pytest.mark.django_db
def test_view_non_existing_unauth_cart(client):
    previousCartCount = len(Cart.objects.all())

    url = reverse('cart')
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'No hay productos' in response.content
    assert currentCartCount == previousCartCount + 1
    assert not Cart.objects.all()[0].client
    assert Cart.objects.all()[0].session_id

@pytest.mark.django_db
def test_view_non_existing_auth_cart(client, regular_user):
    client.force_login(regular_user)
    previousCartCount = len(Cart.objects.all())

    url = reverse('cart')
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'No hay productos' in response.content
    assert currentCartCount == previousCartCount + 1
    assert Cart.objects.all()[0].client
    assert not Cart.objects.all()[0].session_id

@pytest.mark.django_db
def test_add_product_to_existing_cart(client, regular_user, auth_cart, sample_product):
    client.force_login(regular_user)
    previousCartItemsCount = len(CartItem.objects.all())

    size = ProductSize.objects.create(name = '43')
    colour = ProductColour.objects.create(name = 'White')

    url = reverse('add_to_cart', args=[sample_product.pk, colour.pk, size.pk])
    response = client.get(url)

    currentCartItemCount = len(CartItem.objects.all())

    assert response.status_code == 302
    assert "cart" in response.url
    assert currentCartItemCount == previousCartItemsCount + 1

@pytest.mark.django_db
def test_add_product_to_non_existing_cart(client, regular_user, sample_product):
    client.force_login(regular_user)
    previousCartItemsCount = len(CartItem.objects.all())

    size = ProductSize.objects.create(name = '43')
    colour = ProductColour.objects.create(name = 'White')

    url = reverse('add_to_cart', args=[sample_product.pk, colour.pk, size.pk])
    response = client.get(url)

    currentCartItemCount = len(CartItem.objects.all())

    assert response.status_code == 302
    assert "cart" in response.url
    assert currentCartItemCount == previousCartItemsCount + 1
    assert currentCartItemCount == 1

@pytest.mark.django_db
def test_increase_product(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]

    previousQuantity = item.quantity

    url = reverse('update_quantity_ajax', args=[item.pk, 'increase'])
    response = client.get(url)

    item.refresh_from_db()
    currentQuantity = item.quantity

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert currentQuantity == previousQuantity + 1

@pytest.mark.django_db
def test_increase_product_without_more_stock(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]
    item.quantity = 10
    item.save()

    previousQuantity = item.quantity

    url = reverse('update_quantity_ajax', args=[item.pk, 'increase'])
    response = client.get(url)

    item.refresh_from_db()
    currentQuantity = item.quantity

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert currentQuantity == previousQuantity

@pytest.mark.django_db
def test_decrease_product(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]
    item.quantity = 2
    item.save()

    previousQuantity = item.quantity

    url = reverse('update_quantity_ajax', args=[item.pk, 'decrease'])
    response = client.get(url)

    item.refresh_from_db()
    currentQuantity = item.quantity

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert currentQuantity == previousQuantity - 1

@pytest.mark.django_db
def test_delete_product(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]

    url = reverse('update_quantity_ajax', args=[item.pk, 'delete'])
    response = client.get(url)

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert len(auth_cart.items.all()) == 0

@pytest.mark.django_db
def test_create_order_from_cart(client, regular_user, auth_cart):
    client.force_login(regular_user)

    url = reverse('create_order_from_cart')
    response = client.get(url)

    createdOrder = Order.objects.filter(client=regular_user)[0]

    assert response.status_code == 302
    assert "/orders/detail" in response.url
    assert createdOrder
    assert len(createdOrder.items.all()) == 1
    assert len(Cart.objects.all()) == 0

@pytest.mark.django_db
def test_create_order_from_empty_cart(client, regular_user):
    client.force_login(regular_user)

    url = reverse('cart')
    client.get(url)

    url = reverse('create_order_from_cart')
    response = client.get(url)

    assert response.status_code == 302
    assert "cart" in response.url
