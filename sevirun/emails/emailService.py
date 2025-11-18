import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

def send_email(subject, html):
    params = {
        "from": "Sevirun <sevirun@resend.dev>",
        "to": ["recipient@gmail.com"],
        "subject": subject,
        "html": html
    }
    email = resend.Emails.send(params)
