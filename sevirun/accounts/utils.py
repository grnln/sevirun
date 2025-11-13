from django.contrib.auth import get_user_model

def authenticate(email, password):
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
        else:
            return None
    except User.DoesNotExist:
        return None

def obtain_attributes_from_request(request):
    name = request.POST.get("name", "").strip()
    surname = request.POST.get("surname", "").strip()
    phone_number = request.POST.get("phone_number", "").strip()
    address = request.POST.get("address", "").strip()
    city = request.POST.get("city", "").strip()
    postal_code = request.POST.get("postal_code", "").strip()
    return name, surname, phone_number, address, city, postal_code