import pytest
from django.urls import reverse
from orders.models import *
from orders.test_fixtures import *
from users.test_fixtures import *

@pytest.mark.django_db
def test_sales_access_as_unauthenticated(client):
    url = reverse('sales')
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_sales_access_as_non_staff(client, regular_user):
    client.force_login(regular_user)
    url = reverse('sales')
    response = client.get(url)
    
    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_sales_access_as_staff(client, staff_user):
    client.force_login(staff_user)
    url = reverse('sales')
    response = client.get(url)
    assert response.status_code == 200
    assert (b'No hay ventas.' in response.content)

@pytest.mark.django_db
def test_sales_are_delivered_orders(client, staff_user, order_list):
    client.force_login(staff_user)

    url = reverse('sales')
    response = client.get(url)
    
    assert response.status_code == 200
    assert (b'No hay ventas.' not in response.content)
    assert (order_list[0] in response.context['sales'])
    assert (order_list[1] not in response.context['sales'])

@pytest.mark.django_db
def test_prices_are_computed(client, staff_user, order_and_items_list):
    client.force_login(staff_user)

    url = reverse('sales')
    response = client.get(url)

    expected_price = Decimal((55.90 * 2 + 75.00 * 1 + 5.5) * 1.21).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    encoded_price = str(expected_price).replace('.', ',').encode()

    assert response.status_code == 200
    assert encoded_price in response.content
