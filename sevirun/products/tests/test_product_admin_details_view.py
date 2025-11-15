import pytest
from django.urls import reverse
from products.test_fixtures import *
from users.test_fixtures import *

@pytest.mark.django_db
def test_no_cart_and_edit_as_staff(client, sample_product, staff_user):    
    client.force_login(staff_user)

    url = reverse('product_detail', args=[sample_product.id])
    response = client.get(url)

    assert response.status_code == 200
    for key in ('product', 'sizes', 'colours', 'stock_list', 'product_available'):
        assert key in response.context
    assert any(t.name == 'products/product_detail.html' for t in response.templates)
    assert "Añadir al carrito".encode() not in response.content
    assert "Editar".encode() in response.content
