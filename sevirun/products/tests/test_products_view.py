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

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')

    product = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = None,
        is_available = True,
        is_highlighted = False,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product,
        size = size,
        colour = colour
    )
    url = reverse('products')
    response = client.get(url)

    os.remove(base_path / 'media' / 'products' / image.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    assert (response.context['no_filters'] == True)    
    assert (bytearray(product.name, encoding = 'utf-8') in response.content)

@pytest.mark.django_db
def test_products_show_prices(client):
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')

    product = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = False,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product,
        size = size,
        colour = colour
    )
    url = reverse('products')
    response = client.get(url)

    os.remove(base_path / 'media' / 'products' / image.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    assert (response.context['no_filters'] == True)    

    assert (bytearray(product.price.replace('.', ','), encoding = 'utf-8') in response.content)
    assert (bytearray(product.price_on_sale.replace('.', ','), encoding = 'utf-8') in response.content)

@pytest.mark.django_db
def test_products_show_badges(client):
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')

    product = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size,
        colour = colour
    )
    url = reverse('products')
    response = client.get(url)

    os.remove(base_path / 'media' / product.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    assert (response.context['no_filters'] == True)    

    assert (b'Destacado' in response.content)
    assert (b'Disponible' in response.content)
    assert (b'No disponible' in response.content)

@pytest.mark.django_db
def test_products_brand_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size,
        colour = colour
    )
    url = reverse('products')
    response = client.get(url + '?brand=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)
    
@pytest.mark.django_db
def test_products_type_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    product_type_2 = ProductType.objects.create(name = 'Shoes 2')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type_2,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size,
        colour = colour
    )
    url = reverse('products')
    response = client.get(url + '?type=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)

@pytest.mark.django_db
def test_products_model_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    product_type_2 = ProductType.objects.create(name = 'Shoes 2')
    season = ProductSeason.objects.create(name = 'Summer')
    season_2 = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    material_2 = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    size_2 = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')
    colour_2 = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type_2,
        season = season_2,
        material = material_2,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size_2,
        colour = colour_2
    )
    url = reverse('products')
    response = client.get(url + '?model=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)

@pytest.mark.django_db
def test_products_season_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    product_type_2 = ProductType.objects.create(name = 'Shoes 2')
    season = ProductSeason.objects.create(name = 'Summer')
    season_2 = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    material_2 = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    size_2 = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')
    colour_2 = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type_2,
        season = season_2,
        material = material_2,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size_2,
        colour = colour_2
    )
    url = reverse('products')
    response = client.get(url + '?season=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)

@pytest.mark.django_db
def test_products_material_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    product_type_2 = ProductType.objects.create(name = 'Shoes 2')
    season = ProductSeason.objects.create(name = 'Summer')
    season_2 = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    material_2 = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    size_2 = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')
    colour_2 = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type_2,
        season = season_2,
        material = material_2,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size_2,
        colour = colour_2
    )
    url = reverse('products')
    response = client.get(url + '?material=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)

@pytest.mark.django_db
def test_products_size_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    product_type_2 = ProductType.objects.create(name = 'Shoes 2')
    season = ProductSeason.objects.create(name = 'Summer')
    season_2 = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    material_2 = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    size_2 = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')
    colour_2 = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type_2,
        season = season_2,
        material = material_2,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size_2,
        colour = colour_2
    )
    url = reverse('products')
    response = client.get(url + '?size=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)

@pytest.mark.django_db
def test_products_colour_filter(client):
    brand = Brand.objects.create(name = 'Test Brand')
    brand_2 = Brand.objects.create(name = 'Test Brand 2')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_model_2 = ProductModel.objects.create(name = 'Model X 2', brand = brand_2)
    product_type = ProductType.objects.create(name = 'Shoes')
    product_type_2 = ProductType.objects.create(name = 'Shoes 2')
    season = ProductSeason.objects.create(name = 'Summer')
    season_2 = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    material_2 = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[2]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    size = ProductSize.objects.create(name = '37')
    size_2 = ProductSize.objects.create(name = '37')
    colour = ProductColour.objects.create(name = 'Red')
    colour_2 = ProductColour.objects.create(name = 'Red')

    product_1 = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = True,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_1,
        size = size,
        colour = colour
    )

    product_2 = Product.objects.create(
        name = 'Test Product 2',
        short_description = 'Short desc',
        description = 'Long description',
        picture = image,
        price = '19.99',
        price_on_sale = '6.99',
        is_available = False,
        is_highlighted = True,
        created_at = now,
        updated_at = now,
        model = product_model_2,
        type = product_type_2,
        season = season_2,
        material = material_2,
    )

    ProductStock.objects.create(
        stock = 10,
        product = product_2,
        size = size_2,
        colour = colour_2
    )
    url = reverse('products')
    response = client.get(url + '?colour=1')

    os.remove(base_path / 'media' / product_1.picture.name)
    os.remove(base_path / 'media' / product_2.picture.name)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    
    assert (response.context['no_filters'] == False)
    assert (len(response.context['products']) == 1)

    assert (bytearray(product_1.name, encoding = 'utf-8') in response.content)
    assert (bytearray(product_2.name, encoding = 'utf-8') not in response.content)

@pytest.mark.django_db
def test_products_empty(client):
    url = reverse('products')
    response = client.get(url)

    assert (response.status_code == 200)
    
    for key in ('products', 'no_filters'):
        assert key in response.context

    assert any(t.name == 'products_list.html' for t in response.templates)
    assert (b'No hay productos disponibles en este momento.' in response.content)