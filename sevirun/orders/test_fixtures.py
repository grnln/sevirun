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
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    size = ProductSize.objects.create(name = '42')
    colour = ProductColour.objects.create(name = 'Red')

    size2 = ProductSize.objects.create(name = '43')
    colour2 = ProductColour.objects.create(name = 'Blue')

    now = timezone.now()

    sample_product = Product.objects.create(
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
        "product": sample_product,
        "size": size,
        "colour": colour,
        "quantity": 2,
        "unit_price": "55.90"
    })

    OrderItem.objects.create(**{
        "order": delivered_order,
        "product": sample_product,
        "size": size2,
        "colour": colour2,
        "quantity": 1,
        "unit_price": "75.00"
    })

    return delivered_order
