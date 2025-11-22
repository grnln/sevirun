import pytest
from django.urls import reverse
from orders.models import *
from orders.test_fixtures import *
from django.contrib import messages

@pytest.mark.django_db
def test_order_detail_access_as_unauthenticated(client):
    url = reverse('order_detail', args=[1])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_order_detail_access_as_staff(client, staff_user, order_and_items_list):
    client.force_login(staff_user)
    url = reverse('order_detail', args=[1])
    response = client.get(url)
    assert response.status_code == 200
    assert 'states' in response.context

@pytest.mark.django_db
def test_order_detail_access_as_non_owner_client(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('order_detail', args=[2])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('orders')

@pytest.mark.django_db
def test_order_detail_access_as_client_owner(client, regular_user, order_list):
    client.force_login(regular_user)

    url = reverse('order_detail', args=[1])
    response = client.get(url)
    
    assert response.status_code == 200
    assert(response.context['order'].client == regular_user)
    assert not messages.get_messages(response.wsgi_request)

@pytest.mark.django_db
def test_detail_order_does_not_exist(client, regular_user):
    client.force_login(regular_user)

    url = reverse('order_detail', args=[999])
    response = client.get(url)
    
    assert response.status_code == 302
    assert response.url == reverse('orders')

@pytest.mark.django_db
def test_prices_are_computed(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('orders')
    response = client.get(url)

    expected_price = Decimal((55.90 * 2 + 75.00 * 1 + 5.5) * 1.21).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    encoded_price = str(expected_price).replace('.', ',').encode()

    assert response.status_code == 200
    assert encoded_price in response.content

@pytest.mark.django_db
def test_order_detail_shows_size_and_color(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('order_detail', args=[1])
    response = client.get(url)

    assert response.status_code == 200
    assert b'Talla: 42' in response.content
    assert b'Color: Red' in response.content
    assert b'Talla: 43' in response.content
    assert b'Color: Blue' in response.content

@pytest.mark.django_db
def test_order_detail_shows_form_to_staff(client, staff_user, order_and_items_list):
    client.force_login(staff_user)

    url = reverse('order_detail', args = [1])
    response = client.get(url)

    assert response.status_code == 200
    assert b'name = "order-1-state"' in response.content

@pytest.mark.django_db
def test_order_detail_does_not_show_form_to_client(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('order_detail', args = [1])
    response = client.get(url)

    assert response.status_code == 200
    assert b'name = "order-1-state"' not in response.content

@pytest.mark.django_db
def test_order_detail_changes_state_on_staff_post(client, staff_user, order_and_items_list):
    client.force_login(staff_user)

    url = reverse('order_detail', args = [1])
    response = client.post(url, {'order-1-state': 'CA'})

    assert response.status_code == 200
    assert b'name = "order-1-state"' in response.content
    assert b'Cancelado' in response.content
    assert Order.objects.get(pk = 1).state == 'CA'

@pytest.mark.django_db
def test_order_detail_does_not_change_state_on_client_post(client, regular_user, order_and_items_list):
    client.force_login(regular_user)

    url = reverse('order_detail', args = [1])
    response = client.post(url, {'order-1-state': 'CA'})

    assert response.status_code == 200
    assert b'name = "order-1-state"' not in response.content
    assert b'Cancelado' not in response.content
    assert Order.objects.get(pk = 1).state != 'CA'
