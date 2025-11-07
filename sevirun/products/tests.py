import pytest
from django.urls import reverse
from .models import Product, ProductMaterial, ProductSeason, ProductType, ProductModel

@pytest.mark.django_db
def test_product_details_status_and_context(client):

    material = ProductMaterial.objects.create(id=1, name='Cotton')
    season = ProductSeason.objects.create(id=1, name='Summer')
    type = ProductType.objects.create(id=1, name='Shoes')
    model = ProductModel.objects.create(id=1, name='Sneakers')
    
    product = Product.objects.create(
        name='Test Product',
        short_description='This is a test product.',
        description='Detailed description of the test product.',
        picture='products/test.jpg',
        price=9.99,
        price_on_sale=7.99,
        is_available=True,
        is_highlighted=False,
        created_at="2025-01-01T00:00:00.000+01:00",
        updated_at="2025-01-01T00:10:10.000+01:00",
        model=model,
        type=type,
        season=season,
        material=material
    )

    url = reverse('product_detail', args=[product.id])
    response = client.get(url)
    assert response.status_code == 200
    assert 'product' in response.context