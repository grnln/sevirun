from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.db.models import Sum
from .models import Product

def index(request):
    no_filters = True
    products = Product.objects.all()

    brand_filter = request.GET.get('brand', None)
    type_filter = request.GET.get('type', None)
    model_filter = request.GET.get('model', None)
    season_filter = request.GET.get('season', None)
    material_filter = request.GET.get('material', None)
    size_filter = request.GET.get('size', None)
    colour_filter = request.GET.get('colour', None)

    if brand_filter != None:
        model_pks = [m.pk for m in ProductModel.objects.all().filter(brand = brand_filter)]
        products = [p for p in products if p.model.pk in model_pks]
        no_filters = False

    if type_filter != None:
        products = products.filter(type = type_filter)
        no_filters = False

    if model_filter != None:
        products = products.filter(model = model_filter)
        no_filters = False

    if season_filter != None:
        products = products.filter(season = season_filter)
        no_filters = False

    if material_filter != None:
        products = products.filter(material = material_filter)
        no_filters = False

    if size_filter != None:
        products_with_size = [s.product for s in ProductStock.objects.all().filter(size = size_filter)]
        products = [p for p in products if p in products_with_size]
        no_filters = False

    if colour_filter != None:
        products_with_colour = [s.product for s in ProductStock.objects.all().filter(colour = colour_filter)]
        products = [p for p in products if p in products_with_colour]
        no_filters = False

    context = {
        'products': products,
        'no_filters': no_filters
    }
    return render(request, 'products_list.html', context)

def categories(request):
    brands = Brand.objects.all()
    product_types = ProductType.objects.all()
    product_models = ProductModel.objects.all()
    product_seasons = ProductSeason.objects.all()
    product_materials = ProductMaterial.objects.all()
    product_sizes = ProductSize.objects.all()
    product_colours = ProductColour.objects.all()
    
    context = {
        'brands': brands,
        'product_types': product_types,
        'product_models': product_models,
        'product_seasons': product_seasons,
        'product_materials': product_materials,
        'product_sizes': product_sizes,
        'product_colours': product_colours
    }
    return render(request, 'categories.html', context)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    
    sizes = product.productstock_set.values('size__id', 'size__name')\
        .annotate(total=Sum('stock'))\
        .order_by('size__name')

    colours = product.productstock_set.values('colour__id', 'colour__name')\
        .annotate(total=Sum('stock'))\
        .order_by('colour__name')

    stock_list = list(product.productstock_set.values('size_id', 'colour_id', 'stock'))

    context = {
        'product': product,
        'sizes': sizes,
        'colours': colours,
        'stock_list': stock_list,
        'product_available': product.is_available,
    }
    return render(request, 'product_detail.html', context)
