import pytest
from django.urls import reverse
from django.utils import timezone
from collections.abc import Iterable
from products.models import *
from datetime import datetime

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
    brand = Brand.objects.create(name = 'Marca de prueba')
    product_model = ProductModel.objects.create(name = 'Modelo de prueba', brand = brand)
    product_type = ProductType.objects.create(name = 'Tipo de prueba')
    season = ProductSeason.objects.create(name = 'Temporada de prueba')
    material = ProductMaterial.objects.create(name = 'Material de prueba')

    size = ProductSize.objects.create(name = 'Talla de prueba')
    colour = ProductColour.objects.create(name = 'Color de prueba')
    
    product = Product.objects.create(
        name='Zapato de prueba',
        description='Un zapato cómodo',
        picture='products/dummy.png',
        price='49.99',
        is_highlighted = False,
        created_at = timezone.now(),
        updated_at = timezone.now(),
        model = product_model,
        type = product_type,
        season = season,
        material = material
    )
    
    ProductStock.objects.create(
        stock = 0,
        product = product,
        size = size,
        colour = colour
    )
    url = reverse('home')
    resp = client.get(url)

    assert resp.status_code == 200
    assert b'No hay productos destacados disponibles en este momento.' in resp.content


@pytest.mark.django_db
def test_home_shows_products_list_when_present(client):
    brand = Brand.objects.create(name = 'Marca de prueba')
    product_model = ProductModel.objects.create(name = 'Modelo de prueba', brand = brand)
    product_type = ProductType.objects.create(name = 'Tipo de prueba')
    season = ProductSeason.objects.create(name = 'Temporada de prueba')
    material = ProductMaterial.objects.create(name = 'Material de prueba')

    size = ProductSize.objects.create(name = 'Talla de prueba')
    colour = ProductColour.objects.create(name = 'Color de prueba')
    
    product = Product.objects.create(
        name='Zapato de prueba',
        description='Un zapato cómodo',
        picture='products/dummy.png',
        price='49.99',
        is_highlighted = True,
        created_at = timezone.now(),
        updated_at = timezone.now(),
        model = product_model,
        type = product_type,
        season = season,
        material = material
    )
    
    ProductStock.objects.create(
        stock = 10,
        product = product,
        size = size,
        colour = colour
    )
    url = reverse('home')
    resp = client.get(url)

    assert resp.status_code == 200
    assert product.name.encode() in resp.content

@pytest.mark.django_db
def test_about_us_is_shown(client):
    url = reverse('about')
    resp = client.get(url)

    assert resp.status_code == 200
    assert b'Sobre nosotros' in resp.content

@pytest.mark.django_db
def test_contact_is_shown(client):
    url = reverse('contact')
    resp = client.get(url)

    assert resp.status_code == 200
    assert b'Contacta con nosotros' in resp.content