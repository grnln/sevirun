from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum
from .models import Product

# Create your views here.
def index(request):
    return HttpResponse('Vista de productos.')

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    
    sizes = product.productstock_set.values('size__id', 'size__name')\
        .annotate(total=Sum('stock'))\
        .order_by('size__name')

    colours = product.productstock_set.values('colour__id', 'colour__name')\
        .annotate(total=Sum('stock'))\
        .order_by('colour__name')

    # Provide raw stock list for the client-side script to build a combination map
    stock_list = list(product.productstock_set.values('size_id', 'colour_id', 'stock'))

    context = {
        'product': product,
        'sizes': sizes,
        'colours': colours,
        'stock_list': stock_list,
        'product_available': product.is_available,
    }
    return render(request, 'product_detail.html', context)