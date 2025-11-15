from django import forms
from .models import *

def get_brand_choices():
    out = [('null', 'Todas')]
    out.extend([(str(b.pk), b.name) for b in Brand.objects.all()])
    return out

def get_product_type_choices():
    out = [('null', 'Todos')]
    out.extend([(str(t.pk), t.name) for t in ProductType.objects.all()])
    return out

def get_product_season_choices():
    out = [('null', 'Todas')]
    out.extend([(str(s.pk), s.name) for s in ProductSeason.objects.all()])
    return out

def get_product_material_choices():
    out = [('null', 'Todos')]
    out.extend([(str(m.pk), m.name) for m in ProductMaterial.objects.all()])
    return out

def get_product_size_choices():
    out = [('null', 'Todas')]
    out.extend([(str(s.pk), s.name) for s in ProductSize.objects.all()])
    return out

def get_product_colour_choices():
    out = [('null', 'Todos')]
    out.extend([(str(c.pk), c.name) for c in ProductColour.objects.all()])
    return out

class ProductFiltersForm(forms.Form):
    brand = forms.ChoiceField(required = False, label = 'Marca', choices = get_brand_choices)    
    type = forms.ChoiceField(required = False, label = 'Tipo', choices = get_product_type_choices)
    season = forms.ChoiceField(required = False, label = 'Temporada', choices = get_product_season_choices)
    material = forms.ChoiceField(required = False, label = 'Material', choices = get_product_material_choices)
    size = forms.ChoiceField(required = False, label = 'Talla', choices = get_product_size_choices)
    colour = forms.ChoiceField(required = False, label = 'Color', choices = get_product_colour_choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'd-flex form-select'
