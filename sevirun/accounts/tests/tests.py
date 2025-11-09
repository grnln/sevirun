import pytest
from django.urls import reverse

from accounts.backends import User

@pytest.mark.django_db
def test_login_page_renders(client):
    url = reverse('login')
    resp = client.get(url)
    content = resp.content.decode().lower()

    assert resp.status_code == 200
    assert "<form" in content
    assert 'name="email"' in content or 'name="username"' in content
    assert 'name="password"' in content
    assert 'type="submit"' in content


@pytest.mark.django_db
def test_successful_login(client):
    User.objects.create_user(
        email="user1@user.com",
        password="user"
    )
    url = reverse('login')
    resp = client.post(url, {
        "email": "user1@user.com",
        "password": "user"
    })

    assert resp.status_code == 302
    assert resp.url == reverse('home')


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