from django import forms
from .models import *

def get_product_type_choices():
    return [(str(t.pk), t.name) for t in ProductType.objects.all()]

class ProductFiltersForm(forms.Form):
    type = forms.ChoiceField(required = False, label = 'Tipo', choices = get_product_type_choices)