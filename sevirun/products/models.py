from django.db import models

# Brand
class Brand(models.Model):
    name = models.CharField(max_length = 255, null = False)
    logo = models.ImageField(upload_to = 'brands/', null = True)

    def __str__(self):
        return f'{{name: {self.name}, logo: {self.logo}}}'

# Product attributes
class ProductModel(models.Model):
    name = models.CharField(max_length = 32, null = False)
    picture = models.ImageField(upload_to = 'models/', null = True)
    brand = models.ForeignKey(Brand, on_delete = models.CASCADE, null = False)

    def __str__(self):
        return f'{{name: {self.name}, brand: {self.brand.name}}}'

class ProductType(models.Model):
    name = models.CharField(max_length = 16, null = False)
    picture = models.ImageField(upload_to = 'types/', null = True)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductSeason(models.Model):
    name = models.CharField(max_length = 16, null = False)
    picture = models.ImageField(upload_to = 'season/', null = True)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductMaterial(models.Model):
    name = models.CharField(max_length = 16, null = False)
    picture = models.ImageField(upload_to = 'materials/', null = True)

    def __str__(self):
        return f'{{name: {self.name}}}'    

class ProductSize(models.Model):
    name = models.CharField(max_length = 4, null = False)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductColour(models.Model):
    name = models.CharField(max_length = 16, null = False)
    picture = models.ImageField(upload_to = 'colours/', null = True)

    def __str__(self):
        return f'{{name: {self.name}}}'

# Product
class Product(models.Model):
    name = models.CharField(max_length = 255, null = False)
    short_description = models.CharField(null = False, max_length = 255)
    description = models.TextField(null = False)
    picture = models.ImageField(upload_to = 'products/', null = False)

    price = models.DecimalField(max_digits = 6, decimal_places = 2, null = False)
    price_on_sale = models.DecimalField(max_digits = 6, decimal_places = 2, null = True)
    
    is_available = models.BooleanField(null = False)
    is_highlighted = models.BooleanField(null = False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_deleted = models.BooleanField(null = False, default=False)

    # Navigation attributes
    model = models.ForeignKey(ProductModel, on_delete = models.CASCADE, null = False)
    type = models.ForeignKey(ProductType, on_delete = models.CASCADE, null = False)
    season = models.ForeignKey(ProductSeason, on_delete = models.CASCADE, null = False)
    material = models.ForeignKey(ProductMaterial, on_delete = models.CASCADE, null = False)

    def __str__(self):
        return f'''
                {{
                    name: {self.name},
                    description: {self.description},
                    picture: {self.picture},
                    price: {self.price},
                    price_on_sale: {self.price_on_sale},
                    is_available: {self.is_available},
                    is_highlighted: {self.is_highlighted},
                    created_at: {self.created_at},
                    updated_at: {self.updated_at},
                    model: {self.model.name},
                    type: {self.type.name},
                    season: {self.season.name},
                    material: {self.material.name}
                }}
                '''

class ProductStock(models.Model):
    stock = models.PositiveIntegerField(null = False)

    product = models.ForeignKey(Product, on_delete = models.CASCADE, null = False)
    size = models.ForeignKey(ProductSize, on_delete = models.CASCADE, null = False)
    colour = models.ForeignKey(ProductColour, on_delete = models.CASCADE, null = False)

    def __str__(self):
        return f'{{product: {self.product.name}, size: {self.size.name}, colour: {self.colour.name}, stock: {self.stock}}}'
