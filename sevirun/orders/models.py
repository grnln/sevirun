from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from users.models import AppUser
from products.models import Product

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class OrderState(models.TextChoices):
    PENDING = "PE", _("Pendiente")
    PAID = "PA", _("Pagado")
    PROCESSING = "PR", _("En proceso")
    SHIPPED = "SH", _("Enviado")
    DELIVERED = "DE", _("Entregado")
    CANCELLED = "CA", _("Cancelado")

class PaymentMethod(models.TextChoices):
    CREDIT_CARD = "CC", _("Tarjeta de crédito")
    CASH = "CA", _("Contrareembolso")

class ShoeSize(models.IntegerChoices):
    EU_36 = 36, _("EU 36")
    EU_37 = 37, _("EU 37")
    EU_38 = 38, _("EU 38")
    EU_39 = 39, _("EU 39")
    EU_40 = 40, _("EU 40")
    EU_41 = 41, _("EU 41")
    EU_42 = 42, _("EU 42")
    EU_43 = 43, _("EU 43")
    EU_44 = 44, _("EU 44")
    EU_45 = 45, _("EU 45")
    EU_46 = 46, _("EU 46")

class Order(models.Model):
    client = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField(null = False)
    state = models.CharField(choices=OrderState, default=OrderState.PENDING, null=False)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    delivery_cost = models.DecimalField(
        max_digits = 3,
        decimal_places = 2,
        null = False,
        validators=[MinValueValidator(0)]
    )
    discount_percentage = models.DecimalField(
        max_digits = 3,
        decimal_places = 2,
        null = False,
        validators=[MinValueValidator(0), MaxValueValidator(100.00)]
    )
    payment_method = models.CharField(choices=PaymentMethod, default=PaymentMethod.CREDIT_CARD, null=False)
    shipping_address = models.CharField(max_length = 255, null = False, blank=False)
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=17,
        null=False
    )

    @property
    def subtotal(self):
        '''Taxes are assumed to be a 21% of the final price'''
        return (self.total_price + self.delivery_cost) * 1.21 * (100 - self.discount_percentage) / 100

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, null=False, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=False)
    size = models.IntegerField(
        choices=ShoeSize.choices,
        null=False
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)], null=False)
    unit_price = models.DecimalField(max_digits = 6, decimal_places = 2, null = False)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
