from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Vista de productos.')

def product_detail(request, product_id):
    return HttpResponse(f'Detalle del producto {product_id}.')