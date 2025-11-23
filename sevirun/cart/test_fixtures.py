import pytest
from cart.models import *
from products.models import *
from products.test_fixtures import *
from users.test_fixtures import *
import uuid

@pytest.fixture
def delivery_cost():
    delivery_cost = DeliveryCost.objects.create(delivery_cost=Decimal("4.99"))
    return delivery_cost

@pytest.fixture
def create_cart_item(sample_product):
    size = ProductSize.objects.create(name = '42')
    colour = ProductColour.objects.create(name = 'Red')
    ProductStock.objects.create(product=sample_product, size=size, colour=colour, stock=10)
    def _create_cart_item(cart):
        return CartItem.objects.create(
            cart=cart,
            product=sample_product,
            colour=colour,
            size=size,
            quantity=1
        )
    return _create_cart_item

@pytest.fixture
def auth_cart(regular_user, create_cart_item):
    auth_cart = Cart.objects.create(**{
      "client": regular_user,
      "created_at": "2025-01-01T00:00:00.000+01:00",
      "updated_at": "2025-01-01T00:00:00.000+01:00"
    })
    create_cart_item(auth_cart)
    return auth_cart

@pytest.fixture
def unauth_cart(create_cart_item):
    unauth_cart = Cart.objects.create(**{
      "session_id": str(uuid.uuid4()),
      "created_at": "2025-01-01T00:00:00.000+01:00",
      "updated_at": "2025-01-01T00:00:00.000+01:00"
    })
    create_cart_item(unauth_cart)
    return unauth_cart
