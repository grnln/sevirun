from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from users.models import AppUser
from products.models import *
from decimal import Decimal, ROUND_CEILING
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class OrderState(models.TextChoices):
    PENDING = "PE", _("Pendiente de pago")
    PROCESSING = "PR", _("En proceso")
    SHIPPED = "SH", _("Enviado")
    DELIVERED = "DE", _("Entregado")
    CANCELLED = "CA", _("Cancelado")

class PaymentMethod(models.TextChoices):
    CREDIT_CARD = "CC", _("Tarjeta de crédito")
    CASH = "CA", _("Contrareembolso")

class OrderType(models.TextChoices):
    SHOP = "SP", _("En tienda")
    HOME_DELIVERY = "HD", _("A domicilio")

class Order(models.Model):
    client = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null = False)
    state = models.CharField(choices=OrderState, default=OrderState.PENDING, null=False)
    client_email = models.EmailField(validators = [validate_email], null = True, blank = True)
    type = models.CharField(choices=OrderType, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(client__isnull=False) | models.Q(session_id__isnull=False),
                name='order_has_client_or_session'
            )
        ]

    @property
    def subtotal(self):
        result = Decimal(sum(item.total_price for item in self.items.all()))
        return result.quantize(Decimal("0.01"), rounding=ROUND_CEILING)

    delivery_cost = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        null = False,
        validators=[MinValueValidator(0.0)]
    )
    discount_percentage = models.DecimalField(
        max_digits = 5,
        decimal_places = 2,
        null = False,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.00)]
    )
    payment_method = models.CharField(choices=PaymentMethod, default=PaymentMethod.CREDIT_CARD, null=False)
    shipping_address = models.CharField(max_length = 255, null = True, blank=True)
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=17,
        null=True,
        blank=True
    )

    tax_percentage = 21  # IVA

    @property
    def total_price(self):
        subtotal = self.subtotal
        delivery = self.delivery_cost 
        discount = self.discount_percentage 
        result = Decimal((subtotal + delivery) * Decimal(f"1.{int(self.tax_percentage)}") * (100 - discount) / 100)
        return result.quantize(Decimal("0.01"), rounding=ROUND_CEILING)

    @property
    def items_count(self):
        return self.items.count()

    @property
    def total_units(self):
        return sum(item.quantity for item in self.items.all())

    def clean(self):
        super().clean()
        is_pending = self.state == OrderState.PENDING
        
        if not is_pending:
            errors = {}
            
            if not self.shipping_address:
                errors['shipping_address'] = (
                    'Shipping address is required unless order state is pending.'
                )
            
            if not self.phone_number:
                errors['phone_number'] = (
                    'Phone number is required unless order state is pending.'
                )
            
            if errors:
                raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'''
                {{
                    client: {self.client.pk},
                    state: {self.state},
                    delivery_cost: {self.delivery_cost},
                    discount_percentage: {self.discount_percentage},
                    payment_method: {self.payment_method},
                    shipping_address: {self.shipping_address},
                    phone_number: {self.phone_number},
                    total_price: {self.total_price},
                    subtotal: {self.subtotal}
                }}
                '''

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, null=False, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, null=False)
    size = models.ForeignKey(ProductSize, on_delete = models.DO_NOTHING, null = False)
    colour = models.ForeignKey(ProductColour, on_delete = models.DO_NOTHING, null = False)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(99)], null=False)
    unit_price = models.DecimalField(max_digits = 6, decimal_places = 2, null = False)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f'''
                {{
                    order: {self.order.pk},
                    product: {self.product.pk},
                    size: {self.size.pk},
                    colour: {self.colour.pk},
                    quantity: {self.quantity},
                    unit_price: {self.unit_price},
                    total_price: {self.total_price}
                }}
                '''