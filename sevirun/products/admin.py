from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Brand)
admin.site.register(ProductType)
admin.site.register(ProductSeason)
admin.site.register(ProductMaterial)
admin.site.register(ProductModel)
admin.site.register(ProductSize)
admin.site.register(ProductColour)
admin.site.register(Product)
admin.site.register(ProductStock)