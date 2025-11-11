from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.db.models import Sum
from .models import Product
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductFiltersForm

def index(request):
    products = Product.objects.all()
    
    prev_page = request.GET.get('from', '/')
    brand_filter = request.GET.get('brand', None)
    type_filter = request.GET.get('type', None)
    model_filter = request.GET.get('model', None)
    season_filter = request.GET.get('season', None)
    material_filter = request.GET.get('material', None)
    size_filter = request.GET.get('size', None)
    colour_filter = request.GET.get('colour', None)
    search_text = request.GET.get('product-search', None)

    if brand_filter != None and brand_filter != 'null':
        model_pks = [m.pk for m in ProductModel.objects.all().filter(brand = brand_filter)]
        products = products.filter(model__in = model_pks)

    if type_filter != None and type_filter != 'null':
        products = products.filter(type = type_filter)

    if model_filter != None and model_filter != 'null':
        products = products.filter(model = model_filter)

    if season_filter != None and season_filter != 'null':
        products = products.filter(season = season_filter)

    if material_filter != None and material_filter != 'null':
        products = products.filter(material = material_filter)

    if size_filter != None and size_filter != 'null':
        products_with_size = [s.product.pk for s in ProductStock.objects.all().filter(size = size_filter)]
        products = products.filter(pk__in = products_with_size)

    if colour_filter != None and colour_filter != 'null':
        products_with_colour = [s.product.pk for s in ProductStock.objects.all().filter(colour = colour_filter)]
        products = products.filter(pk__in = products_with_colour)

    if search_text != None and search_text != 'null' and search_text != '':
        model_pks = [m.pk for m in ProductModel.objects.all().filter(name__contains = search_text)]
        products_name = products.filter(name__contains = search_text)
        products_model = products.filter(model__in = model_pks)
        products = (products_name | products_model).distinct()
    
    filters = ProductFiltersForm(request.GET)

    context = {
        'products': products,
        'filters': filters,
        'from': prev_page
    }
    return render(request, 'products/products_list.html', context)

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
    return render(request, 'products/categories.html', context)

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
    return render(request, 'products/product_detail.html', context)

def manage_products(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'products/products_list.html', context)

@staff_member_required
def edit_product(request, product_id):
    return HttpResponse("Editar producto - (implementar plantilla)")

@staff_member_required
def create_product(request):
    return HttpResponse("Crear producto - (implementar plantilla)")

@staff_member_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f'El producto "{product_name}" ha sido eliminado correctamente.')
    return redirect("products")
