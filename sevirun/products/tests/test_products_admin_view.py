import pytest
from django.urls import reverse
from products.test_fixtures import *
from users.test_fixtures import *

@pytest.mark.django_db
def test_edit_and_delete_buttons(client, sample_product, staff_user):    
    client.force_login(staff_user)

    url = reverse('products')
    response = client.get(url)

    assert (response.status_code == 200)
    
    for key in ('products', 'filters', 'from'):
        assert key in response.context

    assert any(t.name == 'products/products_list.html' for t in response.templates)
    assert (bytearray(sample_product.name, encoding = 'utf-8') in response.content)
    assert "Editar".encode() in response.content
    assert "Eliminar".encode() in response.content
    assert "Añadir".encode() in response.content
