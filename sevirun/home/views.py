from django.shortcuts import render
from products.models import Product
from django.http import HttpResponse

from products.forms import ProductFiltersForm

def home(request):
    products = Product.objects.all().filter(is_highlighted=True, is_deleted=False)
    context = {
        'products': products,
        'filters': ProductFiltersForm()
    }
    return render(request, 'home/home.html', context)

def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')
