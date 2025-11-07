from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import Product
from .forms import *

def get_product_model_choices_with_brand(brand):
    out = [("None", "Todos")]
    out.extend([(str(m.pk), m.name) for m in ProductModel.objects.all().filter(brand = brand)])
    return out

def index(request):
    products = Product.objects.all()

    if request.method == 'POST':
        filters = ProductFiltersForm(request.POST)

        brand_filter = request.POST.get('brand')
        type_filter = request.POST.get('type')
        model_filter = request.POST.get('model')
        season_filter = request.POST.get('season')
        material_filter = request.POST.get('material')
        size_filter = request.POST.get('size')
        colour_filter = request.POST.get('colour')

        if brand_filter.lower() != 'none':
            filters.fields['model'].choices = get_product_model_choices_with_brand(brand_filter)
            products = products.filter()

        if type_filter.lower() != 'none':
            products = products.filter(type = type_filter)
        
        if model_filter.lower() != 'none':
            products = products.filter(model = model_filter)

        if season_filter.lower() != 'none':
            products = products.filter(season = season_filter)

        if material_filter.lower() != 'none':
            products = products.filter(material = material_filter)

        if size_filter.lower() != 'none':
            products_with_size = [s.product for s in ProductStock.objects.all().filter(size = size_filter)]
            products = [p for p in products if p in products_with_size]

        if colour_filter.lower() != 'none':
            products_with_colour = [s.product for s in ProductStock.objects.all().filter(colour = colour_filter)]
            products = [p for p in products if p in products_with_colour]
    else:
        filters = ProductFiltersForm()

    context = {
        'products': products,
        'filters': filters
    }
    return render(request, 'products_list.html', context)