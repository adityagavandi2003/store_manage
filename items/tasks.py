from celery import shared_task
from twilio.rest import Client
from django.conf import settings
import os

@shared_task
def send_whatsapp_invoice_task(order_id, shop_data, invoice_file_url=None):
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_whatsapp_number = settings.TWILIO_WHATSAPP_FROM
        to_whatsapp_number = f"whatsapp:+91{shop_data['customer_phone']}"
        print("invoice: ",invoice_file_url[0])
        print("shop_data:", shop_data)
        pdf_url = [f"http://localhost:8000/media/invoices/{invoice_file_url[0]}"]
        print(pdf_url)
        client = Client(account_sid, auth_token)

        # Message content
        message_body = f"Hello {shop_data['customer']}, your invoice for Order #{order_id} is ready."

        # Send text message
        client.messages.create(
            body=message_body,
            from_=from_whatsapp_number,
            to=to_whatsapp_number,
        )

        # Send media (if file URL provided)
        if pdf_url:
            client.messages.create(
                media_url=[pdf_url],
                from_=from_whatsapp_number,
                to=to_whatsapp_number
            )

        return True
    except Exception as e:
        print("WhatsApp invoice sending failed:", e)
        return False
