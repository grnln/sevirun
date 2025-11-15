from sqlite3 import IntegrityError

from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from accounts.utils import authenticate

from accounts.utils import obtain_attributes_from_request

User = get_user_model()
# Create your views here.
def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(email = email, password = password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
               messages.error(request, 'Email o contraseña incorrectos')
        return render(request, 'registration/login.html')
    else:
        return redirect('home')

def logout(request):
    auth_logout(request)
    return redirect('home')

def register(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'No ha podido registrarse. Vuelva a intentarlo.')
                return render(request, 'registration/register.html')

            if not password:
                messages.error(request, 'No ha podido registrarse. Vuelva a intentarlo.')
                return render(request, 'registration/register.html')

            try:
                existing_user = User.objects.get(email=email)
            except User.DoesNotExist:
                existing_user = None

            if existing_user is not None:
                messages.error(request, 'Ya existe una cuenta con ese email.')
                return render(request, 'registration/register.html')

            name, surname, phone_number, address, city, postal_code = obtain_attributes_from_request(request)

            try:
                new_user = User.objects.create(
                    name=name,
                    surname=surname,
                    email=email,
                    phone_number=phone_number,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False
                )
                new_user.set_password(password)
                new_user.save()

                login(request, new_user)
                return redirect('home')

            except IntegrityError:
                messages.error(request, 'No ha podido registrarse. Vuelva a intentarlo.')

        return render(request, 'registration/register.html')
    else:
        return redirect('home')


from django.contrib.auth import update_session_auth_hash


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        current_password = request.POST.get("current_password", "").strip()
        new_password = request.POST.get("password", "").strip()

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'El email no es válido.')
            return render(request, 'registration/profile.html')

        if new_password:
            if not current_password:
                messages.error(request, 'Debes ingresar tu contraseña actual para cambiarla.')
                return render(request, 'registration/profile.html')

            if not request.user.check_password(current_password):
                messages.error(request, 'La contraseña actual es incorrecta.')
                return render(request, 'registration/profile.html')

        existing_user = User.objects.filter(email=email).exclude(id=request.user.id).first()
        if existing_user:
            messages.error(request, 'Ya existe una cuenta con ese email.')
            return render(request, 'registration/profile.html')

        name, surname, phone_number, address, city, postal_code = obtain_attributes_from_request(request)

        if not all([name, surname, phone_number, address, city, postal_code]):
            messages.error(request, 'Por favor completa todos los campos requeridos.')
            return render(request, 'registration/profile.html')

        try:
            user = request.user
            user.name = name
            user.surname = surname
            user.phone_number = phone_number
            user.address = address
            user.city = city
            user.postal_code = postal_code
            user.email = email
            if new_password:
                user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Tu perfil se ha actualizado correctamente.')
            return redirect('profile')

        except IntegrityError:
            messages.error(request, 'No ha podido actualizarse el perfil. Vuelva a intentarlo.')
            return render(request, 'registration/profile.html')

    return render(request, 'registration/profile.html')
