import pytest
from django.utils import timezone
from users.models import AppUser
from orders.models import *
from products.models import *

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
def regular_user_2(db):
    user = AppUser.objects.create_user(
        email="regular2@example.com",
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
def order_list(regular_user, regular_user_2):
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
      "client": regular_user_2,
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
        "color": "Red",
        "quantity": 2,
        "unit_price": "55.90"
    })

    OrderItem.objects.create(**{
        "order": delivered_order,
        "product": fakeProduct,
        "size": 43,
        "color": "Blue",
        "quantity": 1,
        "unit_price": "75.00"
    })

    return delivered_order
