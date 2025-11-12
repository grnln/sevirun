import pytest, os
from django.utils import timezone
from orders.models import *
from products.models import *
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.fixture
def sample_product():
    brand = Brand.objects.create(name = 'Test Brand')
    product_model = ProductModel.objects.create(name = 'Model X', brand = brand)
    product_type = ProductType.objects.create(name = 'Shoes')
    season = ProductSeason.objects.create(name = 'Summer')
    material = ProductMaterial.objects.create(name = 'Leather')

    base_path = Path(__file__).resolve().parents[1]
    img_path = base_path / 'static' / 'images' / 'test_image.jpg'
    image_bytes = img_path.read_bytes()
    image = SimpleUploadedFile(img_path.name, image_bytes, content_type = 'image/jpeg')

    now = timezone.now()

    fakeProduct = Product.objects.create(
        name = 'Test Product',
        short_description = 'Short desc',
        description = 'Long description',
        price = '19.99',
        price_on_sale = '6.99',
        picture = image,
        is_available = True,
        is_highlighted = False,
        created_at = now,
        updated_at = now,
        model = product_model,
        type = product_type,
        season = season,
        material = material,
    )

    os.remove(base_path / 'media' / 'products' / image.name)

    return fakeProduct