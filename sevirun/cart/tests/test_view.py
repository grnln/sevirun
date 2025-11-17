import pytest
from django.urls import reverse
from cart.models import *
from cart.test_fixtures import *
from users.test_fixtures import *

@pytest.mark.django_db
def test_view_existing_unauth_cart(client, unauth_cart):
    url = reverse('cart')

    previousCartCount = len(Cart.objects.all())

    session = client.session
    session['cart_session_id'] = unauth_cart.session_id
    session.save()
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'Test Product' in response.content
    assert currentCartCount == 1
    assert previousCartCount == currentCartCount

@pytest.mark.django_db
def test_view_existing_auth_cart(client, regular_user, auth_cart):
    client.force_login(regular_user)
    previousCartCount = len(Cart.objects.all())

    url = reverse('cart')
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'Test Product' in response.content
    assert currentCartCount == 1
    assert previousCartCount == currentCartCount

@pytest.mark.django_db
def test_view_non_existing_unauth_cart(client):
    previousCartCount = len(Cart.objects.all())

    url = reverse('cart')
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'No hay productos' in response.content
    assert currentCartCount == previousCartCount + 1
    assert not Cart.objects.all()[0].client
    assert Cart.objects.all()[0].session_id

@pytest.mark.django_db
def test_view_non_existing_auth_cart(client, regular_user):
    client.force_login(regular_user)
    previousCartCount = len(Cart.objects.all())

    url = reverse('cart')
    response = client.get(url)

    currentCartCount = len(Cart.objects.all())

    assert response.status_code == 200
    assert b'No hay productos' in response.content
    assert currentCartCount == previousCartCount + 1
    assert Cart.objects.all()[0].client
    assert not Cart.objects.all()[0].session_id

@pytest.mark.django_db
def test_add_product_to_existing_cart(client, regular_user, auth_cart, sample_product):
    client.force_login(regular_user)
    previousCartItemsCount = len(CartItem.objects.all())

    size = ProductSize.objects.create(name = '43')
    colour = ProductColour.objects.create(name = 'White')

    url = reverse('add_to_cart', args=[sample_product.pk, colour.pk, size.pk])
    response = client.get(url)

    currentCartItemCount = len(CartItem.objects.all())

    assert response.status_code == 302
    assert "cart" in response.url
    assert currentCartItemCount == previousCartItemsCount + 1

@pytest.mark.django_db
def test_add_product_to_non_existing_cart(client, regular_user, sample_product):
    client.force_login(regular_user)
    previousCartItemsCount = len(CartItem.objects.all())

    size = ProductSize.objects.create(name = '43')
    colour = ProductColour.objects.create(name = 'White')

    url = reverse('add_to_cart', args=[sample_product.pk, colour.pk, size.pk])
    response = client.get(url)

    currentCartItemCount = len(CartItem.objects.all())

    assert response.status_code == 302
    assert "cart" in response.url
    assert currentCartItemCount == previousCartItemsCount + 1
    assert currentCartItemCount == 1

@pytest.mark.django_db
def test_increase_product(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]

    previousQuantity = item.quantity

    url = reverse('update_quantity_ajax', args=[item.pk, 'increase'])
    response = client.get(url)

    item.refresh_from_db()
    currentQuantity = item.quantity

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert currentQuantity == previousQuantity + 1

@pytest.mark.django_db
def test_decrease_product(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]
    item.quantity = 2
    item.save()

    previousQuantity = item.quantity

    url = reverse('update_quantity_ajax', args=[item.pk, 'decrease'])
    response = client.get(url)

    item.refresh_from_db()
    currentQuantity = item.quantity

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert currentQuantity == previousQuantity - 1

@pytest.mark.django_db
def test_delete_product(client, regular_user, auth_cart):
    client.force_login(regular_user)
    item = auth_cart.items.all()[0]

    url = reverse('update_quantity_ajax', args=[item.pk, 'delete'])
    response = client.get(url)

    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert len(auth_cart.items.all()) == 0