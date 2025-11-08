import pytest
from django.urls import reverse
from orders.models import *
from users.models import AppUser
from products.models import *
from django.core.files.uploadedfile import SimpleUploadedFile
from pathlib import Path
from django.utils import timezone

@pytest.fixture
def staff_user(db):
    user = AppUser.objects.create_user(
        email="staff@example.com",
        name="Staff",
        surname="User",
        phone_number="+34123456789",
        address="Test Street 1",
        city="City",
        postal_code="12345",
        password="test123",
        is_staff=True
    )
    return user

@pytest.fixture
def regular_user(db):
    user = AppUser.objects.create_user(
        email="regular@example.com",
        name="Regular",
        surname="User",
        phone_number="+34123456789",
        address="Test Street 1",
        city="City",
        postal_code="12345",
        password="test123",
        is_staff=False
    )
    return user

@pytest.fixture
def order_list(regular_user):
    delivered_order = {
        "client": regular_user,
        "created_at": "2025-01-01T00:00:00.000+01:00",
        "state": "DE",
        "delivery_cost": "5.5",
        "discount_percentage": "10.0",
        "payment_method": "CC",
        "shipping_address": "Fake street, 123, 12345, City, Country",
        "phone_number": "+341234356789"
    }
    not_delivered_order = {
      "client": regular_user,
      "created_at": "2025-01-01T00:00:00.000+01:00",
      "state": "PE",
      "delivery_cost": "5.5",
      "discount_percentage": "10.0",
      "payment_method": "CC",
      "shipping_address": "Fake street, 123, 12345, City, Country",
      "phone_number": "+341234356789"
    }

    order1 = Order.objects.create(**delivered_order)
    order2 = Order.objects.create(**not_delivered_order)
    return [order1, order2]

@pytest.fixture
def order_and_items_list(order_list):
    delivered_order = order_list[0]
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    now = timezone.now()

    fakeProduct = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = False,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    OrderItem.objects.create(**{
        "order": delivered_order,
        "product": fakeProduct,
        "size": 42,
        "quantity": 2,
        "unit_price": "55.90"
    })

    return delivered_order

@pytest.mark.django_db
def test_sales_access_as_unauthenticated(client):
    url = reverse('sales')
    response = client.get(url)

    assert response.status_code == 302
    assert "/login" in response.url

@pytest.mark.django_db
def test_sales_access_as_non_staff(client, regular_user):
    client.force_login(regular_user)
    url = reverse('sales')
    response = client.get(url)
    
    assert response.status_code == 302
    assert "/login" in response.url

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

    expected_price = Decimal((55.90 * 2 + 5.5) * 1.21 * 0.9).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    encoded_price = str(expected_price).replace('.', ',').encode()

    assert response.status_code == 200
    assert encoded_price in response.content
