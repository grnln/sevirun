import pytest
from django.urls import reverse
from users.test_fixtures import *
from products.test_fixtures import *
from products.models import *

@pytest.mark.django_db
def test_product_delete_access_as_unauthenticated(client, sample_product):
    url = reverse('delete_product', args=[sample_product.id])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_product_delete_access_as_non_staff(client, regular_user, sample_product):
    client.force_login(regular_user)
    url = reverse('delete_product', args=[sample_product.id])
    response = client.get(url)

    assert response.status_code == 302
    assert "accounts/login" in response.url

@pytest.mark.django_db
def test_product_delete_access_as_staff(client, staff_user, sample_product):
    client.force_login(staff_user)
    url = reverse('delete_product', args=[sample_product.id])
    response = client.get(url)

    assert response.status_code == 200
    assert (b'Eliminar el producto' in response.content)

@pytest.mark.django_db
def test_product_delete(client, staff_user, sample_product):
    client.force_login(staff_user)
    url = reverse('delete_product', args=[sample_product.id])

    client.post(url, follow=True)
    sample_product.refresh_from_db()
    assert sample_product.is_deleted
