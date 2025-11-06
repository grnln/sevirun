from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import Product
from .forms import *

def index(request):
    products = Product.objects.all()

    if request.method == 'POST':
        filters = ProductFiltersForm(request.POST)
        products = products.filter(type = request.POST.get('type'))
    else:
        filters = ProductFiltersForm()

    context = {
        'products': products,
        'filters': filters
    }
    return render(request, 'products_list.html', context)