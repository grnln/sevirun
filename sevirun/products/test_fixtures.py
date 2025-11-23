import pytest, os
from django.utils import timezone
from orders.models import *
from products.models import *
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def test_product_image():
    base_path = Path(__file__).resolve().parents[1]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')
    return image

@pytest.fixture
def remove_image():
    def _remove(imageDir):
        image_path = Path(__file__).resolve().parents[1] / 'media' / str(imageDir)
        os.remove(image_path)
    return _remove

@pytest.fixture
def sample_product_attributes():
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')
    return [product_model, product_type, season, material]

@pytest.fixture
def sample_product(test_product_image, remove_image, sample_product_attributes):
    [product_model, product_type, season, material] = sample_product_attributes
    now = timezone.now()

    fakeProduct = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        price = Decimal('19.99'),
        price_on_sale = Decimal('6.99'),
        picture = test_product_image,
        is_highlighted = False,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    remove_image(fakeProduct.picture)

    return fakeProduct

@pytest.fixture
def valid_product(sample_product_attributes, test_product_image):
    [product_model, product_type, season, material] = sample_product_attributes
    data = {
        'name': 'Created product',
        'short_description': 'This is a short description',
        'description': 'This is a description',
        'price': '100.00',
        'price_on_sale': '49.99',
        'picture': test_product_image,
        'is_highlighted': 'False',
        'model': f'{product_model.id}',
        'type': f'{product_type.id}',
        'season': f'{season.id}',
        'material': f'{material.id}',
    }
    return data
