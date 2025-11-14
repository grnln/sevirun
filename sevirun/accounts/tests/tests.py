import pytest
from django.urls import reverse

from accounts.backends import User

user_data = {
    "email": "newuser@user.com",
    "password": "newuser",
    "name": "new",
    "surname": "user",
    "phone_number": "123456789",
    "address": "Sample address",
    "city": "Sample Town",
    "postal_code": "38678"
}

@pytest.mark.django_db
def test_login_page_renders(client):
    url = reverse('login')
    resp = client.get(url)
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "<form" in content
    assert 'name="email"' in content
    assert 'name="password"' in content
    assert 'type="submit"' in content

@pytest.mark.django_db
def test_register_page_renders(client):
    url = reverse('register')
    resp = client.get(url)
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "<form" in content
    assert 'name="email"' in content
    assert 'name="password"' in content
    assert 'name="name"' in content
    assert 'name="surname"' in content
    assert 'name="phone_number"' in content
    assert 'name="address"' in content
    assert 'name="city"' in content
    assert 'name="postal_code"' in content
    assert 'type="submit"' in content

@pytest.mark.django_db
def test_successful_login(client):
    url = reverse('login')
    resp = client.post(url, {
        "email": "user1@user.com",
        "password": "user"
    })

    assert resp.status_code == 200

@pytest.mark.django_db
def test_successful_register(client):
    url = reverse('register')
    resp = client.post(url, user_data)

    assert resp.status_code == 302


@pytest.mark.django_db
def test_failed_login(client):
    url = reverse('login')
    resp = client.post(url, {
        "email": "wrong@email.com",
        "password": "wrong_password"
    })
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "email o contraseña incorrectos" in content
    assert not resp.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_failed_register(client):
    url = reverse('register')
    resp = client.post(url, {
        "email": "wrongemail",
        "password": "",
    })
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "no ha podido registrarse. vuelva a intentarlo." in content
    assert not resp.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_authenticated_user_redirects(client):
    user = User.objects.create_user(
        email="user1@user.com",
        password="user"
    )
    client.force_login(user)
    url = reverse('login')
    resp = client.get(url)

    assert resp.status_code == 302
    assert resp.url == reverse('home')
    assert resp.wsgi_request.user.is_authenticated

    url = reverse('register')
    resp = client.get(url)

    assert resp.status_code == 302
    assert resp.url == reverse('home')
    assert resp.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_logout(client):
    user = User.objects.create_user(
        email="user1@user.com",
        password="user"
    )
    client.force_login(user)
    url = reverse('logout')
    resp = client.get(url)

    assert resp.status_code == 302
    assert resp.url == reverse('home')

    resp = client.get(reverse('home'))
    assert not resp.wsgi_request.user.is_authenticated

@pytest.mark.django_db
def test_profile_page_renders(client):
    user = User.objects.create_user(
        email="user1@user.com",
        password="user"
    )
    client.force_login(user)
    url = reverse('profile')
    resp = client.get(url)
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "<form" in content
    assert 'name="email"' in content
    assert 'name="password"' in content
    assert 'name="name"' in content
    assert 'name="surname"' in content
    assert 'name="phone_number"' in content
    assert 'name="address"' in content
    assert 'name="city"' in content
    assert 'name="postal_code"' in content
    assert 'name="current_password"' in content
    assert 'type="submit"' in content

@pytest.mark.django_db
def test_successful_profile_update(client):
    user = User.objects.create_user(
        email="user1@user.com",
        password="user"
    )
    client.force_login(user)
    url = reverse('profile')
    modified_user_data = user_data
    modified_user_data["email"] = "user3@user.com"
    resp = client.post(url, modified_user_data)

    assert resp.status_code == 200


@pytest.mark.django_db
def test_profile_update_existing_email_fails(client):
    User.objects.create_user(
        email="user1@user.com",
        password="password123"
    )

    user2 = User.objects.create_user(
        email="user2@user.com",
        password="password456"
    )

    client.force_login(user2)

    url = reverse('profile')
    modified_user_data = user_data.copy()

    modified_user_data["email"] = "user1@user.com"
    modified_user_data["password"] = ""

    resp = client.post(url, modified_user_data)
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "ya existe una cuenta con ese email" in content