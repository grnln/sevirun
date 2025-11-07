import pytest, os

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from pathlib import Path

from products.models import *

@pytest.mark.django_db
def test_products_status_and_context(client):
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    size = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')

    url = reverse('categories')
    response = client.get(url)

    assert (response.status_code == 200)
    
    for key in ('brands', 'product_types', 'product_models', 'product_seasons', 'product_materials', 'product_sizes', 'product_colours'):
        assert key in response.context

    assert any(t.name == 'categories.html' for t in response.templates)

    assert (len(response.context['brands']) == 1)
    assert (len(response.context['product_types']) == 1)
    assert (len(response.context['product_models']) == 1)
    assert (len(response.context['product_seasons']) == 1)
    assert (len(response.context['product_materials']) == 1)
    assert (len(response.context['product_sizes']) == 1)
    assert (len(response.context['product_colours']) == 1)

    assert (bytearray(brand.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_model.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_type.name, encoding = 'utf-8') in response.content)
    assert (bytearray(season.name, encoding = 'utf-8') in response.content)
    assert (bytearray(material.name, encoding = 'utf-8') in response.content)
    assert (bytearray(size.name, encoding = 'utf-8') in response.content)
    assert (bytearray(colour.name, encoding = 'utf-8') in response.content)

@pytest.mark.django_db
def test_products_status_and_context(client):
    url = reverse('categories')
    response = client.get(url)

    assert (response.status_code == 200)
    
    for key in ('brands', 'product_types', 'product_models', 'product_seasons', 'product_materials', 'product_sizes', 'product_colours'):
        assert key in response.context

    assert any(t.name == 'categories.html' for t in response.templates)

    assert (len(response.context['brands']) == 0)
    assert (len(response.context['product_types']) == 0)
    assert (len(response.context['product_models']) == 0)
    assert (len(response.context['product_seasons']) == 0)
    assert (len(response.context['product_materials']) == 0)
    assert (len(response.context['product_sizes']) == 0)
    assert (len(response.context['product_colours']) == 0)

    assert (b'No hay marcas registradas en el sistema.' in response.content)
    assert (b'No hay tipos de producto registrados en el sistema.' in response.content)
    assert (b'No hay modelos registrados en el sistema.' in response.content)
    assert (b'No hay temporadas registradas en el sistema.' in response.content)
    assert (b'No hay materiales registrados en el sistema.' in response.content)
    assert (b'No hay tallas registradas en el sistema.' in response.content)
    assert (b'No hay colores registrados en el sistema.' in response.content)
