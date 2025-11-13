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

@pytest.mark.django_db
def test_product_edit(client, staff_user, valid_product, sample_product, remove_image):
    client.force_login(staff_user)
    url = reverse('edit_product', args=[sample_product.id])

    allProductsPrevious = Product.objects.all()
    client.post(url, {**valid_product, 'id': '999'}, follow=True)
    
    updated = Product.objects.filter(name=valid_product['name']).first()
    allProducts = Product.objects.all()

    remove_image(updated.picture.name)

    assert updated is not None
    assert updated.id == sample_product.id
    assert len(allProducts) == len(allProductsPrevious)

@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_to_remove",
    [
        "name",
        "short_description",
        "description",
        "price",
        "price_on_sale",
        "is_available",
        "is_highlighted",
        "model",
        "type",
        "season",
        "material",
    ]
)
def test_product_edit_with_null_values(client, staff_user, valid_product, sample_product, field_to_remove, remove_image):
    client.force_login(staff_user)
    url = reverse('edit_product', args=[sample_product.id])

    edited_product = valid_product.copy()
    edited_product.pop(field_to_remove)

    client.post(url, edited_product, follow=True)
    updated = Product.objects.get(id=sample_product.id)
    remove_image(updated.picture.name)

    assert updated is not None
    assert getattr(updated, field_to_remove) == getattr(sample_product, field_to_remove)
    
