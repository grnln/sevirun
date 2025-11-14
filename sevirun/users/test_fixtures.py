import pytest
from users.models import AppUser

@pytest.fixture
def staff_user(db):
    user = AppUser.objects.create_user(
        email="staff@example.com",
        name="Staff",
        surname="User",
        phone_number="+34123456789",
        address="Test Street 1",
        city="City",
        postal_code="12345",
        password="test123",
        is_staff=True
    )
    return user

@pytest.fixture
def regular_user(db):
    user = AppUser.objects.create_user(
        email="regular@example.com",
        name="Regular",
        surname="User",
        phone_number="+34123456789",
        address="Test Street 1",
        city="City",
        postal_code="12345",
        password="test123",
        is_staff=False
    )
    return user

@pytest.fixture
def regular_user_2(db):
    user = AppUser.objects.create_user(
        email="regular2@example.com",
        name="Regular",
        surname="User",
        phone_number="+34123456789",
        address="Test Street 1",
        city="City",
        postal_code="12345",
        password="test123",
        is_staff=False
    )
    return user
