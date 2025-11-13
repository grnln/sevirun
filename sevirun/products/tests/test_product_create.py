import pytest
from django.urls import reverse
from users.test_fixtures import *
from products.test_fixtures import *
from products.models import *

@pytest.mark.django_db
def test_product_create_access_as_unauthenticated(client):
    url = reverse('create_product')
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_product_create_access_as_non_staff(client, regular_user):
    client.force_login(regular_user)
    url = reverse('create_product')
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_product_create_access_as_staff(client, staff_user):
    client.force_login(staff_user)
    url = reverse('create_product')
    response = client.get(url)

    assert response.status_code == 200
    assert (b'Crear Producto' in response.content)

@pytest.mark.django_db
def test_product_create(client, staff_user, valid_product, remove_image):
    client.force_login(staff_user)
    url = reverse('create_product')
    client.post(url, valid_product, follow=True)

    created = Product.objects.filter(name=valid_product['name']).first()
    remove_image(created.picture.name)

    assert created is not None

@pytest.mark.django_db
def test_product_create_with_null_values(client, staff_user, valid_product):
    client.force_login(staff_user)
    url = reverse('create_product')

    for key in valid_product:
        invalid_product = valid_product.copy()
        if key in ("price_on_sale", "is_available", "is_highlighted"):
            continue
        invalid_product.pop(key)
        client.post(url, invalid_product, follow=True)
        created = Product.objects.filter(name=valid_product['name']).first() if key != 'name' else Product.objects.filter(description=valid_product['description']).first()
        assert created is None
