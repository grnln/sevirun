from django.db import models
from users.models import AppUser
from products.models import *
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

# Create your models here.

class Cart(models.Model):
    client = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(client__isnull=False) | models.Q(session_id__isnull=False),
                name='cart_has_client_or_session'
            )
        ]
        
    @property
    def temp_subtotal(self):
        allItems = self.items.all()
        temp_price = 0
        for item in allItems:
            item_price = item.product.price_on_sale if item.product.price_on_sale else item.product.price
            temp_price += item.quantity * item_price
        return temp_price

    def __str__(self):
        return f'''
                {{
                    client: {self.client.pk if self.client else "anonymous"},
                    items: {[str(item) for item in self.items.all()]}
                }}
                '''

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=False, related_name="items")
    colour = models.ForeignKey(ProductColour, on_delete=models.DO_NOTHING, null=False)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=False)
    size = models.ForeignKey(ProductSize, on_delete = models.DO_NOTHING, null = False)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)], null=False)

    @property
    def temp_price(self):
        temp_price = self.product.price_on_sale if self.product.price_on_sale else self.product.price
        return temp_price * self.quantity

    def __str__(self):
        return f'''
                {{
                    cart: {self.cart.pk},
                    product: {self.product.pk},
                    size: {self.size.pk},
                    quantity: {self.quantity},
                    colour: {self.colour}
                }}
                '''