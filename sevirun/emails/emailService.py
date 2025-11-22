import os
import resend
from decimal import Decimal
from django.template.loader import render_to_string

resend.api_key = os.environ["RESEND_API_KEY"]

def send_email(subject, html):
    params = {
        "from": "Sevirun <sevirun@resend.dev>",
        "to": ["ignaciomorap04@gmail.com"],
        "subject": subject,
        "html": html
    }
    email = resend.Emails.send(params)

def send_order_confirmation_email(order, tracking_url):
    html_content = render_to_string('emails/order_finished.html', {
        'order': order,
        'discount_amount': Decimal(order.subtotal + order.delivery_cost) * Decimal(order.discount_percentage) * Decimal(0.01),
        'tax_amount': Decimal(order.subtotal + order.delivery_cost) * Decimal(100 - order.discount_percentage) * Decimal(order.tax_percentage) * Decimal(0.0001),
        'tracking_url': tracking_url
    })
    send_email("Your order has been confirmed", html_content)
