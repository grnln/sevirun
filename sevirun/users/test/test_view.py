import pytest
from django.urls import reverse
from django.contrib.messages import get_messages

from users.models import AppUser


@pytest.mark.django_db
def test_admin_users_view_get_as_staff(client):
    staff_user = AppUser.objects.create_user(
        email='admin@example.com', password='adminpass', name='Admin', surname='User',
        phone_number='123', address='addr', city='city', postal_code='0000', is_staff=True
    )

    user = AppUser.objects.create_user(
        email='user@example.com', password='userpass', name='Normal', surname='User',
        phone_number='456', address='addr2', city='city2', postal_code='1111'
    )

    client.force_login(staff_user)
    url = reverse('admin_users')
    resp = client.get(url)
    assert resp.status_code == 200
    assert user.email.encode() in resp.content


@pytest.mark.django_db
def test_admin_users_view_redirects_non_staff(client):
    non_staff = AppUser.objects.create_user(
        email='nons@example.com', password='p', name='No', surname='Body',
        phone_number='0', address='', city='', postal_code=''
    )
    client.force_login(non_staff)
    url = reverse('admin_users')
    resp = client.get(url)
    assert resp.status_code == 302


@pytest.mark.django_db
def test_admin_edit_user_get_and_post(client):
    staff_user = AppUser.objects.create_user(
        email='admin2@example.com', password='adminpass', name='Admin', surname='User',
        phone_number='123', address='addr', city='city', postal_code='0000', is_staff=True
    )

    user = AppUser.objects.create_user(
        email='user2@example.com', password='userpass', name='Normal', surname='User',
        phone_number='456', address='addr2', city='city2', postal_code='1111'
    )

    client.force_login(staff_user)
    url = reverse('admin_edit_user', args=[user.id])
    # GET
    resp = client.get(url)
    assert resp.status_code == 200

    # POST update
    resp = client.post(url, {
        'name': 'Updated',
        'surname': 'Person',
        'email': user.email,
        'phone_number': '999',
        'address': 'new addr',
        'city': 'new city',
        'postal_code': '2222',
        'password': 'newpass',
    }, follow=True)

    user.refresh_from_db()
    assert user.name == 'Updated'
    assert user.check_password('newpass')


@pytest.mark.django_db
def test_admin_create_user_get_and_post(client):
    staff_user = AppUser.objects.create_user(
        email='admin3@example.com', password='adminpass', name='Admin', surname='User',
        phone_number='123', address='addr', city='city', postal_code='0000', is_staff=True
    )

    client.force_login(staff_user)
    url = reverse('admin_create_user')
    # GET
    resp = client.get(url)
    assert resp.status_code == 200

    # POST create
    resp = client.post(url, {
        'name': 'Created',
        'surname': 'One',
        'email': 'created@example.com',
        'phone_number': '111',
        'address': 'addr3',
        'city': 'c3',
        'postal_code': '3333',
        'password': 'createdpass',
        'is_staff': '1',
    }, follow=True)

    created = AppUser.objects.filter(email='created@example.com').first()
    assert created is not None
    assert created.check_password('createdpass')
    assert created.is_staff


@pytest.mark.django_db
def test_admin_delete_user_get_and_post(client):
    staff_user = AppUser.objects.create_user(
        email='admin4@example.com', password='adminpass', name='Admin', surname='User',
        phone_number='123', address='addr', city='city', postal_code='0000', is_staff=True
    )

    to_delete = AppUser.objects.create_user(
        email='todelete@example.com', password='todelete', name='To', surname='Delete',
        phone_number='7', address='', city='', postal_code=''
    )

    client.force_login(staff_user)
    url = reverse('admin_delete_user', args=[to_delete.id])
    # GET confirm
    resp = client.get(url)
    assert resp.status_code == 200

    # POST delete
    resp = client.post(url, follow=True)
    assert not AppUser.objects.filter(email='todelete@example.com').exists()


@pytest.mark.django_db
def test_unauthenticated_redirects(client):
    url = reverse('admin_users')
    resp = client.get(url)
    assert resp.status_code == 302
    assert '/accounts/login/' in resp.url

@pytest.mark.django_db
def test_unauthenticated_redirects_edit(client):
    url = reverse('admin_edit_user', args=[1])
    resp = client.get(url)
    assert resp.status_code == 302
    assert '/accounts/login/' in resp.url

@pytest.mark.django_db
def test_unauthenticated_redirects_delete(client):
    url = reverse('admin_delete_user', args=[1])
    resp = client.get(url)
    assert resp.status_code == 302
    assert '/accounts/login/' in resp.url

@pytest.mark.django_db
def test_unauthenticated_redirects_create(client):
    url = reverse('admin_create_user')
    resp = client.get(url)
    assert resp.status_code == 302
    assert '/accounts/login/' in resp.url


@pytest.mark.django_db
def test_create_validation_missing_fields_shows_error(client):
    staff = AppUser.objects.create_user(
        email='staffv@example.com', password='p', name='S', surname='T',
        phone_number='1', address='', city='', postal_code='', is_staff=True
    )
    client.force_login(staff)
    url = reverse('admin_create_user')

    resp = client.post(url, {'name': 'X'}, follow=True)

    assert not AppUser.objects.filter(name='X').exists()

    msgs = [str(m) for m in get_messages(resp.wsgi_request)]
    assert any('completa los campos obligatorios' in m for m in msgs)


@pytest.mark.django_db
def test_duplicate_email_on_create(client):
    staff = AppUser.objects.create_user(
        email='staffdup@example.com', password='p', name='S', surname='T',
        phone_number='1', address='', city='', postal_code='', is_staff=True
    )
    existing = AppUser.objects.create_user(email='dup@example.com', password='p', name='E', surname='X', phone_number='0', address='', city='', postal_code='')
    client.force_login(staff)

    create_url = reverse('admin_create_user')
    resp = client.post(create_url, {
        'name': 'Created',
        'surname': 'One',
        'email': existing.email,
        'phone_number': '111',
        'address': 'addr3',
        'city': 'c3',
        'postal_code': '3333',
        'password': 'x',
        'is_staff': '0',
    }, follow=True)
    msgs = [str(m) for m in get_messages(resp.wsgi_request)]
    assert any('Ya existe un usuario' in m or 'Ya existe un usuario con ese correo electrónico' in m for m in msgs)

@pytest.mark.django_db
def test_duplicate_email_on_edit(client):
    staff = AppUser.objects.create_user(
        email='staffdup@example.com', password='p', name='S', surname='T',
        phone_number='1', address='', city='', postal_code='', is_staff=True
    )
    existing = AppUser.objects.create_user(email='dup@example.com', password='p', name='E', surname='X', phone_number='0', address='', city='', postal_code='')
    client.force_login(staff)

    other = AppUser.objects.create_user(email='other@example.com', password='p', name='O', surname='K', phone_number='2', address='', city='', postal_code='')
    edit_url = reverse('admin_edit_user', args=[other.id])
    resp = client.post(edit_url, {'email': existing.email}, follow=True)
    msgs = [str(m) for m in get_messages(resp.wsgi_request)]
    assert any('El correo ya está en uso' in m for m in msgs)
    
    other.refresh_from_db()
    assert other.email == 'other@example.com'
    



@pytest.mark.django_db
def test_list_view_context_contains_users_queryset(client):
    staff = AppUser.objects.create_user(email='staff@example.com', password='p', name='S', surname='T', phone_number='1', address='', city='', postal_code='', is_staff=True)
    u1 = AppUser.objects.create_user(email='user1@example.com', password='p', name='A', surname='B', phone_number='0', address='', city='', postal_code='')
    client.force_login(staff)
    resp = client.get(reverse('admin_users'))
    assert resp.status_code == 200
    assert 'users' in resp.context
    assert u1 in resp.context['users']

@pytest.mark.django_db
def test_edit_without_password_does_not_change_password(client):
    staff = AppUser.objects.create_user(email='staff@example.com', password='p', name='S', surname='T', phone_number='1', address='', city='', postal_code='', is_staff=True)
    user = AppUser.objects.create_user(email='user@example.com', password='oldpass', name='P', surname='W', phone_number='3', address='', city='', postal_code='')
    client.force_login(staff)
    resp = client.post(reverse('admin_edit_user', args=[user.id]), {
        'name': 'P2', 'surname': 'W2', 'email': user.email
    }, follow=True)
    user.refresh_from_db()
    assert user.check_password('oldpass')