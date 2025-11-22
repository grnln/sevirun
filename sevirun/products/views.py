from django.shortcuts import render
from .models import *
from django.db.models import Sum
from .models import Product
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductFiltersForm
from django.urls import reverse

def index(request):
    products = Product.objects.filter(is_deleted=False)
    
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
    product = get_object_or_404(Product, pk=product_id)
    
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

@staff_member_required(login_url='login')
def edit_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)

            if request.POST.get('model'):
                product.model = get_object_or_404(ProductModel, id=request.POST.get('model'))
            if request.POST.get('type'):
                product.type = get_object_or_404(ProductType, id=request.POST.get('type'))
            if request.POST.get('season'):
                product.season = get_object_or_404(ProductSeason, id=request.POST.get('season'))
            if request.POST.get('material'):
                product.material = get_object_or_404(ProductMaterial, id=request.POST.get('material'))

            fields = {
                'name': request.POST.get('name'),
                'short_description': request.POST.get('short_description'),
                'description': request.POST.get('description'),
                'price': request.POST.get('price'),
                'price_on_sale': request.POST.get('price_on_sale'),
            }
            
            for field, value in fields.items():
                if value:
                    setattr(product, field, value)
            
            product.is_highlighted = request.POST.get('is_highlighted', False) == 'on'
            
            if 'picture' in request.FILES:
                product.picture = request.FILES['picture']

            product.save()
            messages.success(request, f'Producto "{product.name}" editado correctamente.')
            return redirect('products')
        
        except Exception as e:
            messages.error(request, f'Error al crear el producto: {str(e)}')
            
    return render_create_edit_form(request, product=get_object_or_404(Product, id=product_id), is_editing=True)

@staff_member_required(login_url='login')
def create_product(request):
    if request.method == 'POST':
        try:
            model = get_object_or_404(ProductModel, id=request.POST.get('model'))
            product_type = get_object_or_404(ProductType, id=request.POST.get('type'))
            season = get_object_or_404(ProductSeason, id=request.POST.get('season'))
            material = get_object_or_404(ProductMaterial, id=request.POST.get('material'))
            
            data = {
                'name': request.POST.get('name'),
                'short_description': request.POST.get('short_description'),
                'description': request.POST.get('description'),
                'picture': request.FILES.get('picture'),
                'price': request.POST.get('price'),
                'price_on_sale': request.POST.get('price_on_sale') or None,
                'is_highlighted': 'is_highlighted' in request.POST,
                'model': model,
                'type': product_type,
                'season': season,
                'material': material,
            }
            
            required = ['name', 'short_description', 'description', 'picture', 'price', 'model', 'type', 'season', 'material']
            if not all(data.get(field) for field in required):
                messages.error(request, 'Por favor, completa todos los campos obligatorios.')
                return redirect('create_product')
            
            product = Product(**data)
            product.save()
            messages.success(request, f'Producto "{product.name}" creado correctamente.')
            return redirect('products')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('create_product')
    return render_create_edit_form(request)

def render_create_edit_form(request, product=None, is_editing=False):
    context = {
        'models': ProductModel.objects.all(),
        'types': ProductType.objects.all(),
        'seasons': ProductSeason.objects.all(),
        'materials': ProductMaterial.objects.all(),
        'is_editing': is_editing,
        'product': product
    }
    return render(request, 'products/create_edit_product.html', context)

def render_product_attribute_edit(request, attribute, attribute_name, has_logo = False, has_picture = False, has_brand = False):
    brands = []
    if has_brand:
        brands = Brand.objects.all()
    context = {
        'attribute': attribute,
        'attribute_name': attribute_name,
        'has_logo': has_logo,
        'has_picture': has_picture,
        'brands': brands
    }
    return render(request, 'products/edit_product_attribute.html', context)

@staff_member_required(login_url='login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product_name = product.name
        product.is_deleted = True
        product.save()
        messages.success(request, f'El producto "{product_name}" ha sido eliminado correctamente.')
        return redirect('products')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@staff_member_required(login_url='login')
def catalog_management(request):

    return render(request, 'products/catalog_management.html', {
        'brands': Brand.objects.all(),
        'models': ProductModel.objects.all(),
        'types': ProductType.objects.all(),
        'materials': ProductMaterial.objects.all(),
        'sizes': ProductSize.objects.all(),
        'colours': ProductColour.objects.all()
    })

@staff_member_required(login_url='login')
def create_brand(request):
    if request.method == "POST":
        name = request.POST.get("brandName")
        if name:
            Brand.objects.create(name=name)
        return redirect(f"{reverse('catalog_management')}?tab=brands")
    
    return redirect('catalog_management')

@staff_member_required(login_url='login')
def create_model(request):
    if request.method == "POST":
        name = request.POST.get("modelName")
        brand = request.POST.get("brandSelect")
        if name and brand:
            brandObject = get_object_or_404(Brand, pk=int(brand))
            ProductModel.objects.create(name=name, brand=brandObject)
        return redirect(f"{reverse('catalog_management')}?tab=models")
    
    return redirect('catalog_management')

@staff_member_required(login_url='login')
def create_type(request):
    if request.method == "POST":
        name = request.POST.get("typeName")
        if name:
            ProductType.objects.create(name=name)
        return redirect(f"{reverse('catalog_management')}?tab=types")
    
    return redirect('catalog_management')

@staff_member_required(login_url='login')
def create_material(request):
    if request.method == "POST":
        name = request.POST.get("materialName")
        if name:
            ProductMaterial.objects.create(name=name)
        return redirect(f"{reverse('catalog_management')}?tab=materials")
    
    return redirect('catalog_management')

@staff_member_required(login_url='login')
def create_size(request):
    if request.method == "POST":
        name = request.POST.get("sizeName")
        if name:
            ProductSize.objects.create(name=name)
        return redirect(f"{reverse('catalog_management')}?tab=sizes")
    
    return redirect('catalog_management')

@staff_member_required(login_url='login')
def create_colour(request):
    if request.method == "POST":
        name = request.POST.get("colourName")
        if name:
            ProductColour.objects.create(name=name)
        return redirect(f"{reverse('catalog_management')}?tab=colours")
    
    return redirect('catalog_management')

@staff_member_required(login_url='login')
def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, pk=brand_id)
    if(len(brand.models.all()) > 0):
        messages.error(request, 'Existen modelos de producto que son de esta marca!')
        return redirect(f"{reverse('catalog_management')}?tab=brands")
    brand.delete()
    return redirect(f"{reverse('catalog_management')}?tab=brands")

@staff_member_required(login_url='login')
def delete_model(request, model_id):
    model = get_object_or_404(ProductModel, pk=model_id)
    if(len(model.products) > 0):
        messages.error(request, 'Existen productos que son de este modelo!')
        return redirect(f"{reverse('catalog_management')}?tab=models")
    model.delete()
    return redirect(f"{reverse('catalog_management')}?tab=models")

@staff_member_required(login_url='login')
def delete_type(request, type_id):
    type = get_object_or_404(ProductType, pk=type_id)
    if(len(type.products) > 0):
        messages.error(request, 'Existen productos que son de este tipo!')
        return redirect(f"{reverse('catalog_management')}?tab=types")
    type.delete()
    return redirect(f"{reverse('catalog_management')}?tab=types")

@staff_member_required(login_url='login')
def delete_material(request, material_id):
    material = get_object_or_404(ProductMaterial, pk=material_id)
    if(len(material.products) > 0):
        messages.error(request, 'Existen productos que usan este material!')
        return redirect(f"{reverse('catalog_management')}?tab=materials")
    material.delete()
    return redirect(f"{reverse('catalog_management')}?tab=materials")

@staff_member_required(login_url='login')
def delete_size(request, size_id):
    size = get_object_or_404(ProductSize, pk=size_id)
    if(size.product_count > 0):
        messages.error(request, 'Existen productos que usan esta talla!')
        return redirect(f"{reverse('catalog_management')}?tab=sizes")
    size.delete()
    return redirect(f"{reverse('catalog_management')}?tab=sizes")

@staff_member_required(login_url='login')
def delete_colour(request, colour_id):    
    colour = get_object_or_404(ProductColour, pk=colour_id)
    if(colour.product_count > 0):
        messages.error(request, 'Existen productos que usan este color!')
        return redirect(f"{reverse('catalog_management')}?tab=colours")
    colour.delete()
    return redirect(f"{reverse('catalog_management')}?tab=colours")
    
@staff_member_required(login_url='login')
def edit_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    if request.method == 'POST':
        try:            
            if request.POST.get('name'):
                setattr(brand, 'name', request.POST.get('name'))

            if 'logo' in request.FILES:
                brand.logo = request.FILES['logo']

            brand.save()
            messages.success(request, f'Marca "{brand.name}" editada correctamente.')
            return redirect(f"{reverse('catalog_management')}?tab=brands")
        
        except Exception as e:
            messages.error(request, f'Error al crear la marca: {str(e)}')
            
    return render_product_attribute_edit(request, brand, 'marca', has_logo=True)

@staff_member_required(login_url='login')
def edit_model(request, model_id):
    model = get_object_or_404(ProductModel, id=model_id)
    if request.method == 'POST':
        try:            
            if request.POST.get('name'):
                setattr(model, 'name', request.POST.get('name'))

            if request.POST.get('brand'):
                model.brand = get_object_or_404(Brand, id=request.POST.get('brand'))

            if 'picture' in request.FILES:
                model.picture = request.FILES['picture']

            model.save()
            messages.success(request, f'Modelo "{model.name}" editado correctamente.')
            return redirect(f"{reverse('catalog_management')}?tab=models")
        
        except Exception as e:
            messages.error(request, f'Error al crear el modelo: {str(e)}')
            
    return render_product_attribute_edit(request, model, 'modelo', has_picture=True, has_brand=True)

@staff_member_required(login_url='login')
def edit_type(request, type_id):
    type = get_object_or_404(ProductType, id=type_id)
    if request.method == 'POST':
        try:            
            if request.POST.get('name'):
                setattr(type, 'name', request.POST.get('name'))

            if 'picture' in request.FILES:
                type.picture = request.FILES['picture']

            type.save()
            messages.success(request, f'Tipo "{type.name}" editado correctamente.')
            return redirect(f"{reverse('catalog_management')}?tab=types")
        
        except Exception as e:
            messages.error(request, f'Error al crear el tipo: {str(e)}')
            
    return render_product_attribute_edit(request, type, 'tipo', has_picture=True)

@staff_member_required(login_url='login')
def edit_material(request, material_id):
    material = get_object_or_404(ProductMaterial, id=material_id)
    if request.method == 'POST':
        try:            
            if request.POST.get('name'):
                setattr(material, 'name', request.POST.get('name'))

            if 'picture' in request.FILES:
                material.picture = request.FILES['picture']

            material.save()
            messages.success(request, f'Material "{material.name}" editado correctamente.')
            return redirect(f"{reverse('catalog_management')}?tab=materials")
        
        except Exception as e:
            messages.error(request, f'Error al crear el material: {str(e)}')
            
    return render_product_attribute_edit(request, material, 'material', has_picture=True)

@staff_member_required(login_url='login')
def edit_size(request, size_id):
    size = get_object_or_404(ProductSize, id=size_id)
    if request.method == 'POST':
        try:            
            if request.POST.get('name'):
                setattr(size, 'name', request.POST.get('name'))

            size.save()
            messages.success(request, f'Talla "{size.name}" editada correctamente.')
            return redirect(f"{reverse('catalog_management')}?tab=sizes")
        
        except Exception as e:
            messages.error(request, f'Error al crear la talla: {str(e)}')
            
    return render_product_attribute_edit(request, size, 'talla')

@staff_member_required(login_url='login')
def edit_colour(request, colour_id):    
    colour = get_object_or_404(ProductColour, id=colour_id)
    if request.method == 'POST':
        try:            
            if request.POST.get('name'):
                setattr(colour, 'name', request.POST.get('name'))
                        
            if 'picture' in request.FILES:
                colour.picture = request.FILES['picture']

            colour.save()
            messages.success(request, f'Color "{colour.name}" editado correctamente.')
            return redirect(f"{reverse('catalog_management')}?tab=colours")
        
        except Exception as e:
            messages.error(request, f'Error al crear el color: {str(e)}')
            
    return render_product_attribute_edit(request, colour, 'color', has_picture=True)