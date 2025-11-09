from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect

from accounts.utils import authenticate

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
            email = request.POST.get("email")
            existing_user = User.objects.get(email = email)
            try:
                existing_user = User.objects.get(email=email)
            except User.DoesNotExist:
                existing_user = None
            if existing_user is not None:
                messages.error(request, 'Ya existe una cuenta con ese email.')
                return render(request, 'registration/register.html')
            name = request.POST.get("name")
            surname = request.POST.get("surname")
            phone_number = request.POST.get("phone_number")
            address = request.POST.get("address")
            city = request.POST.get("city")
            postal_code = request.POST.get("postal_code")
            password = request.POST.get("password")
            new_user = User.objects.create(name = name, surname = surname, email = email, phone_number = phone_number,
                                           address = address, city = city, postal_code = postal_code, is_active =True,
                                           is_staff = False, is_superuser = False)
            new_user.set_password(password)
            new_user.save()
            if new_user is not None:
                login(request, new_user)
                return redirect('home')
            else:
                messages.error(request, 'No ha podido registrarse. Vuelva a intentarlo.')
        return render(request, 'registration/register.html')
    else:
        return redirect('home')
