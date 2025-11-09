from django.shortcuts import render
from .models import *
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@staff_member_required
def index_sales(request):
    sales = Order.objects.filter(state="DE")
    return render(request, 'sales_list.html', { "sales" : sales })
