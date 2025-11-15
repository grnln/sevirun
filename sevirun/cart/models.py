from django.db import models
from users.models import AppUser
from products.models import *
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

# Create your models here.

class Cart(models.Model):
    client = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'''
                {{
                    client: {self.client.pk},
                    items: {[str(item) for item in self.items.all()]}
                }}
                '''

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=False)
    size = models.ForeignKey(ProductSize, on_delete = models.DO_NOTHING, null = False)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)], null=False)

    def __str__(self):
        return f'''
                {{
                    cart: {self.cart.pk},
                    product: {self.product.pk},
                    size: {self.size.pk},
                    quantity: {self.quantity},
                }}
                '''