import pytest
from django.urls import reverse
from collections.abc import Iterable
from home.models import Product

@pytest.mark.django_db
def test_home_status_and_context(client):
    url = reverse('home')
    resp = client.get(url)

    assert resp.status_code == 200
    assert 'products' in resp.context

    products = resp.context['products']
    assert isinstance(products, Iterable)


@pytest.mark.django_db
def test_home_shows_no_products_message(client):
    url = reverse('home')
    resp = client.get(url)

    assert resp.status_code == 200
    assert b'No hay productos destacados disponibles en este momento.' in resp.content

@pytest.mark.django_db
def test_home_shows_no_featured_products_message(client):
    Product.objects.create(
        title='Zapato de prueba',
        description='Un zapato cómodo',
        image='products/dummy.png',
        price='49.99',
        featured=False,
    )
    
    url = reverse('home')
    resp = client.get(url)

    assert resp.status_code == 200
    assert b'No hay productos destacados disponibles en este momento.' in resp.content


@pytest.mark.django_db
def test_home_shows_products_list_when_present(client):
    product = Product.objects.create(
        title='Zapato de prueba',
        description='Un zapato cómodo',
        image='products/dummy.png',
        price='49.99',
        featured=True,
    )

    url = reverse('home')
    resp = client.get(url)

    assert resp.status_code == 200
    assert product.title.encode() in resp.content