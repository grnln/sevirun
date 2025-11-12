import pytest
from orders.models import *
from products.models import *
from products.test_fixtures import *
from users.test_fixtures import *

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
def order_and_items_list(order_list, sample_product):
    delivered_order = order_list[0]

    OrderItem.objects.create(**{
        "order": delivered_order,
        "product": sample_product,
        "size": 42,
        "quantity": 2,
        "unit_price": "55.90"
    })

    return delivered_order
