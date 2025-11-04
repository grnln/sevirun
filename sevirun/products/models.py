from django.db import models

# Brand
class Brand(models.Model):
    name = models.CharField(max_length = 255)
    logo = models.URLField()

    def __str__(self):
        return f'{{name: {self.name}, logo: {self.logo}}}'

# Product attributes
class ProductType(models.Model):
    name = models.CharField(max_length = 16)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductSeason(models.Model):
    name = models.CharField(max_length = 16)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductMaterial(models.Model):
    name = models.CharField(max_length = 16)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductModel(models.Model):
    name = models.CharField(max_length = 32)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductSize(models.Model):
    name = models.CharField(max_length = 4)

    def __str__(self):
        return f'{{name: {self.name}}}'

class ProductColour(models.Model):
    name = models.CharField(max_length = 16)

    def __str__(self):
        return f'{{name: {self.name}}}'

# Product
class Product(models.Model):
    name = models.CharField(max_length = 255)
    description = models.TextField()
    picture = models.URLField()

    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    price_on_sale = models.DecimalField(max_digits = 6, decimal_places = 2)
    
    is_available = models.BooleanField()
    is_highlighted = models.BooleanField()
    
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    # Navigation attributes
    type = models.ForeignKey(ProductType, on_delete = models.CASCADE)
    season = models.ForeignKey(ProductSeason, on_delete = models.CASCADE)
    material = models.ForeignKey(ProductMaterial, on_delete = models.CASCADE)

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
                    type: {self.type.name},
                    season: {self.season.name},
                    material: {self.material.name}
                }}
                '''
        
class ProductModelStock(models.Model):
    stock = models.IntegerField()

    # Navigation attributes
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    model = models.ForeignKey(ProductModel, on_delete = models.CASCADE)

    def __str__(self):
        return f'{{product: {self.product.name}, model: {self.model.name}, stock: {self.stock}}}'

class ProductSizeStock(models.Model):
    stock = models.IntegerField()

    # Navigation attributes
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete = models.CASCADE)

    def __str__(self):
        return f'{{product: {self.product.name}, size: {self.size.name}, stock: {self.stock}}}'

class ProductColourStock(models.Model):
    stock = models.IntegerField()

    # Navigation attributes
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    colour = models.ForeignKey(ProductColour, on_delete = models.CASCADE)

    def __str__(self):
        return f'{{product: {self.product.name}, colour: {self.colour.name}, stock: {self.stock}}}'
