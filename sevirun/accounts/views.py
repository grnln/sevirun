from django.contrib.auth import login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect

from accounts.utils import authenticate


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