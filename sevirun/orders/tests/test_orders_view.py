import pytest
from django.urls import reverse
from orders.models import *
from orders.test_fixtures import *

@pytest.mark.django_db
def test_orders_access_as_unauthenticated(client):
    url = reverse('orders')
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_sales_access_as_non_staff(client, regular_user):
    client.force_login(regular_user)
    url = reverse('orders')
    response = client.get(url)
    
    assert response.status_code == 200

@pytest.mark.django_db
def test_sales_access_as_staff(client, staff_user):
    client.force_login(staff_user)
    url = reverse('orders')
    response = client.get(url)
    assert response.status_code == 200
    assert 'states' in response.context

@pytest.mark.django_db
def test_orders_are_of_client(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.get(url)
    
    assert response.status_code == 200
    for order in response.context['orders']:
        assert(order.client == regular_user)

@pytest.mark.django_db
def test_no_orders(client, regular_user):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.get(url)
    
    assert response.status_code == 200
    assert (b'No tienes pedidos.' in response.content)

@pytest.mark.django_db
def test_prices_are_computed(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.get(url)

    expected_price = Decimal((55.90 * 2 + 75.00 * 1 + 5.5) * 1.21 * 0.9).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    encoded_price = str(expected_price).replace('.', ',').encode()

    assert response.status_code == 200
    assert encoded_price in response.content

@pytest.mark.django_db
def test_orders_show_form_to_staff(client, staff_user, order_and_items_list):
    client.force_login(staff_user)

    url = reverse('orders')
    response = client.get(url)

    assert response.status_code == 200
    assert b'name = "order-1-state"' in response.content
    assert b'name = "order-2-state"' in response.content

@pytest.mark.django_db
def test_orders_do_not_show_form_to_client(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.get(url)

    assert response.status_code == 200
    assert b'name = "order-1-state"' not in response.content
    assert b'name = "order-2-state"' not in response.content

@pytest.mark.django_db
def test_orders_change_state_on_staff_post(client, staff_user, order_and_items_list):
    client.force_login(staff_user)

    url = reverse('orders')
    response = client.post(url, {'order-1-state': 'CA'})

    assert response.status_code == 200
    assert b'name = "order-1-state"' in response.content
    assert b'Cancelado' in response.content
    assert Order.objects.get(pk = 1).state == 'CA'

@pytest.mark.django_db
def test_orders_do_not_change_state_on_client_post(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.post(url, {'order-1-state': 'CA'})

    assert response.status_code == 200
    assert b'name = "order-1-state"' not in response.content
    assert b'Cancelado' not in response.content
    assert Order.objects.get(pk = 1).state != 'CA'

@pytest.mark.django_db
def test_orders_change_multiple_states_on_staff_post(client, staff_user, order_and_items_list):
    client.force_login(staff_user)

    url = reverse('orders')
    response = client.post(url, {'order-1-state': 'CA', 'order-2-state': 'SH'})

    assert response.status_code == 200
    assert b'name = "order-1-state"' in response.content
    assert b'name = "order-2-state"' in response.content
    assert b'Cancelado' in response.content
    assert b'Enviado' in response.content
    assert Order.objects.get(pk = 1).state == 'CA'
    assert Order.objects.get(pk = 2).state == 'SH'

@pytest.mark.django_db
def test_orders_do_not_change_multiple_states_on_client_post(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.post(url, {'order-1-state': 'CA', 'order-2-state': 'SH'})

    assert response.status_code == 200
    assert b'name = "order-1-state"' not in response.content
    assert b'name = "order-2-state"' not in response.content
    assert b'Cancelado' not in response.content
    assert b'Enviado' not in response.content
    assert Order.objects.get(pk = 1).state != 'CA'
    assert Order.objects.get(pk = 2).state != 'SH'
