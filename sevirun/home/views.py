from django.shortcuts import render
from .models import Product
from django.http import HttpResponse

def home(request):
    products = Product.objects.all().filter(featured=True)
    context = {
        'products': products,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# Placeholder views - remove when implementing actual functionality
def shop(request):
    return HttpResponse("Tienda — listado de productos (implementar plantilla)")

def collections(request):
    return HttpResponse("Colecciones — (implementar plantilla)")

def product_detail(request, pk):
    return HttpResponse(f"Detalle producto {pk} — (implementar plantilla)")

def cart(request):
    return HttpResponse("Carrito — (implementar plantilla)")

def login_view(request):
    return HttpResponse("Login — (implementar plantilla)")
