import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from pathlib import Path

from products.models import (
    Product,
    ProductMaterial,
    ProductSeason,
    ProductType,
    ProductModel,
    Brand,
    ProductSize,
    ProductColour,
    ProductStock,
)

@pytest.mark.django_db
def test_product_details_status_and_context(client):
    brand = Brand.objects.create(name='Test Brand')
    product_model = ProductModel.objects.create(name='Model X', brand=brand)
    ptype = ProductType.objects.create(name='Shoes')
    season = ProductSeason.objects.create(name='Summer')
    material = ProductMaterial.objects.create(name='Leather')

    img_path = Path(__file__).resolve().parents[2] / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type='image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name='37')
    colour = ProductColour.objects.create(name='Red')

    product = Product.objects.create(
        name='Test Product',
        short_description='Short desc',
        description='Long description',
        picture=image,
        price='19.99',
        price_on_sale=None,
        is_available=True,
        is_highlighted=False,
        created_at=now,
        updated_at=now,
        model=product_model,
        type=ptype,
        season=season,
        material=material,
    )

    ProductStock.objects.create(
        stock=10,
        product=product,
        size=size,
        colour=colour
    )

    url = reverse('product_detail', args=[product.id])
    response = client.get(url)
    assert response.status_code == 200
    for key in ('product', 'sizes', 'colours', 'stock_list', 'product_available'):
        assert key in response.context
    assert any(t.name == 'product_detail.html' for t in response.templates)


@pytest.mark.django_db
def test_sizes_colours_and_stock_list(client):
    brand = Brand.objects.create(name='Brand')
    model = ProductModel.objects.create(name='Model', brand=brand)
    ptype = ProductType.objects.create(name='Type')
    season = ProductSeason.objects.create(name='Season')
    material = ProductMaterial.objects.create(name='Material')

    now = timezone.now()
    img_path = Path(__file__).resolve().parents[2] / 'static' / 'images' / 'test_image.jpg'
    image = SimpleUploadedFile(img_path.name, img_path.read_bytes(), content_type='image/jpeg')

    product = Product.objects.create(
        name='Product 2',
        short_description='Short description',
        description='Long description',
        picture=image,
        price=10.00,
        price_on_sale=None,
        is_available=True,
        is_highlighted=False,
        created_at=now,
        updated_at=now,
        model=model,
        type=ptype,
        season=season,
        material=material,
    )

    size_37 = ProductSize.objects.create(name='37')
    size_38 = ProductSize.objects.create(name='38')
    colour_red = ProductColour.objects.create(name='Red')
    colour_blue = ProductColour.objects.create(name='Blue')

    ProductStock.objects.create(product=product, size=size_37, colour=colour_red, stock=2)
    ProductStock.objects.create(product=product, size=size_38, colour=colour_blue, stock=1)

    url = reverse('product_detail', args=[product.id])
    response = client.get(url)

    sizes = list(response.context['sizes'])
    colours = list(response.context['colours'])
    stock_list = response.context['stock_list']

    totals_by_name = {s['size__name']: s['total'] for s in sizes}
    assert totals_by_name.get('37') == 2
    assert totals_by_name.get('38') == 1

    totals_by_colour = {c['colour__name']: c['total'] for c in colours}
    assert totals_by_colour.get('Red') == 2
    assert totals_by_colour.get('Blue') == 1

    # stock_list entries should reflect the created stocks
    assert any(item['size_id'] == size_37.id and item['colour_id'] == colour_red.id and item['stock'] == 2 for item in stock_list)
    assert any(item['size_id'] == size_38.id and item['colour_id'] == colour_blue.id and item['stock'] == 1 for item in stock_list)


@pytest.mark.django_db
def test_price_on_sale_display(client):
    brand = Brand.objects.create(name='Brand Sale')
    model = ProductModel.objects.create(name='Model Sale', brand=brand)
    ptype = ProductType.objects.create(name='Type Sale')
    season = ProductSeason.objects.create(name='Season Sale')
    material = ProductMaterial.objects.create(name='Material Sale')

    now = timezone.now()
    img_path = Path(__file__).resolve().parents[2] / 'static' / 'images' / 'test_image.jpg'
    image = SimpleUploadedFile(img_path.name, img_path.read_bytes(), content_type='image/jpeg')

    product = Product.objects.create(
        name='Product Sale',
        short_description='Short desc sale',
        description='Long desc sale',
        picture=image,
        price=50.00,
        price_on_sale=30.00,
        is_available=True,
        is_highlighted=False,
        created_at=now,
        updated_at=now,
        model=model,
        type=ptype,
        season=season,
        material=material,
    )

    url = reverse('product_detail', args=[product.id])
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()

    assert "30,00" in content  # Price on sale should be displayed
    assert "50,00" in content  # Original price should also be displayed

@pytest.mark.django_db
def test_unavailable_product_display(client):
    brand = Brand.objects.create(name='Brand Unavailable')
    model = ProductModel.objects.create(name='Model Unavailable', brand=brand)
    ptype = ProductType.objects.create(name='Type Unavailable')
    season = ProductSeason.objects.create(name='Season Unavailable')
    material = ProductMaterial.objects.create(name='Material Unavailable')

    now = timezone.now()
    img_path = Path(__file__).resolve().parents[2] / 'static' / 'images' / 'test_image.jpg'
    image = SimpleUploadedFile(img_path.name, img_path.read_bytes(), content_type='image/jpeg')

    product = Product.objects.create(
        name='Product Unavailable',
        short_description='Short desc unavailable',
        description='Long desc unavailable',
        picture=image,
        price=40.00,
        price_on_sale=None,
        is_available=False,
        is_highlighted=False,
        created_at=now,
        updated_at=now,
        model=model,
        type=ptype,
        season=season,
        material=material,
    )

    url = reverse('product_detail', args=[product.id])
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()

    assert 'No disponible' in content
