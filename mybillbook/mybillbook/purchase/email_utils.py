# email_utils.py
from django.core.mail import EmailMessage
from django.conf import settings
import os
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

def send_purchase_email(
    recipient_email,
    purchase_pdf_path,
    purchase_no,
    purchase_id,
    business_name=None,
    party_name=None
):
    subject = f'Purchase #{purchase_no} from {business_name or "Your Company"}'

    # ✅ Tracking pixel URL for purchases
    tracking_pixel_url = f'https://backend-3-2y61.onrender.com/track-email-open?doc_type=Purchase&doc_id={purchase_id}'

    html_message = f'''
    <html>
    <body>
        <p>Dear {party_name or "Valued Customer"},</p>

        <p>Thank you for your business with {business_name or "our company"}.
        Please find attached the purchase #{purchase_no} for your recent transaction.</p>

        <p><strong>Purchase Details:</strong><br>
        - Purchase Number: {purchase_no}<br>
        - Date: {datetime.now().strftime("%d-%m-%Y")}<br>
        - Customer Name: {party_name or "N/A"}</p>

        <p>If you have any questions or concerns regarding this purchase, please don't hesitate to contact us.</p>

        <p><strong>Payment Terms:</strong><br>
        - Please ensure payment is made within the specified due date<br>
        - For any payment-related queries, please contact our accounts department</p>

        <p>Thank you for choosing {business_name or "our company"} for your business needs.</p>

        <p>Best regards,<br>
        {business_name or "Your Company"}<br>
        Accounts Department</p>

        <img src="{tracking_pixel_url}" width="1" height="1" style="display:none;" alt="."/>
    </body>
    </html>
    '''

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
        headers={
            'X-Priority': '1',
            'X-MSMail-Priority': 'High',
            'X-Mailer': 'Microsoft Outlook Express 6.00.2900.2869',
            'X-MimeOLE': 'Produced By Microsoft MimeOLE V6.00.2900.2869',
        }
    )

    email.attach_alternative(html_message, "text/html")

    with open(purchase_pdf_path, 'rb') as f:
        email.attach(f'purchase_{purchase_no}.pdf', f.read(), 'application/pdf')

    email.send()


def send_payment_out_email(recipient_email, payment_out_pdf_path, payment_out_number, business_name=None, party_name=None):
    subject = f'payment_out #{payment_out_number} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{payment_out_number} for your recent purchase.

Payment Out Details:
- Payment Out Number: {payment_out_number}
- Date: {datetime.now().strftime("%d-%m-%Y")}
- Customer Name: {party_name or "N/A"}

If you have any questions or concerns regarding this invoice, please don't hesitate to contact us.

Payment Terms:
- Please ensure payment is made within the specified due date
- For any payment-related queries, please contact our accounts department

Thank you for choosing {business_name or "our company"} for your business needs.

Best regards,
{business_name or "Your Company"}
Accounts Department
'''
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email]
    )
    
    # Set email headers for better quality
    email.extra_headers = {
        'X-Priority': '1',  # High priority
        'X-MSMail-Priority': 'High',
        'X-Mailer': 'Microsoft Outlook Express 6.00.2900.2869',
        'X-MimeOLE': 'Produced By Microsoft MimeOLE V6.00.2900.2869',
        'Content-Transfer-Encoding': 'binary'
    }
    
    # Attach the PDF with high quality settings
    with open(payment_out_pdf_path, 'rb') as f:
        email.attach(
            f'payment_out_{payment_out_number}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_purchasereturn_email(recipient_email, purchasereturn_pdf_path, purchasereturn_no, business_name=None, party_name=None):
    subject = f'purchasereturn #{purchasereturn_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{purchasereturn_no} for your recent purchase.

Invoice Details:
- Invoice Number: {purchasereturn_no}
- Date: {datetime.now().strftime("%d-%m-%Y")}
- Customer Name: {party_name or "N/A"}

If you have any questions or concerns regarding this invoice, please don't hesitate to contact us.

Payment Terms:
- Please ensure payment is made within the specified due date
- For any payment-related queries, please contact our accounts department

Thank you for choosing {business_name or "our company"} for your business needs.

Best regards,
{business_name or "Your Company"}
Accounts Department
'''
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email]
    )
    
    # Set email headers for better quality
    email.extra_headers = {
        'X-Priority': '1',  # High priority
        'X-MSMail-Priority': 'High',
        'X-Mailer': 'Microsoft Outlook Express 6.00.2900.2869',
        'X-MimeOLE': 'Produced By Microsoft MimeOLE V6.00.2900.2869',
        'Content-Transfer-Encoding': 'binary'
    }
    
    # Attach the PDF with high quality settings
    with open(purchasereturn_pdf_path, 'rb') as f:
        email.attach(
            f'salesreturn_{purchasereturn_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()

def send_debitnote_email(
    recipient_email,
    debitnote_pdf_path,
    debitnote_no,
    debitnote_id,
    business_name=None,
    party_name=None
):
    subject = f'Debit Note #{debitnote_no} from {business_name or "Your Company"}'

    # ✅ Replace this with production domain when deploying
    tracking_pixel_url = f'https://backend-3-2y61.onrender.com/track-email-open?doc_type=DebitNote&doc_id={debitnote_id}'

    html_message = f'''
    <html>
    <body>
        <p>Dear {party_name or "Valued Customer"},</p>

        <p>Thank you for your business with {business_name or "our company"}.
        Please find attached the Debit Note #{debitnote_no} related to your account.</p>

        <p><strong>Debit Note Details:</strong><br>
        - Debit Note Number: {debitnote_no}<br>
        - Date: {datetime.now().strftime("%d-%m-%Y")}<br>
        - Customer Name: {party_name or "N/A"}</p>

        <p>If you have any questions or concerns regarding this note, please don't hesitate to contact us.</p>

        <p><strong>Payment Terms:</strong><br>
        - Please ensure any due adjustments are processed as agreed<br>
        - For any queries, contact our accounts department</p>

        <p>Thank you for choosing {business_name or "our company"}.</p>

        <p>Best regards,<br>
        {business_name or "Your Company"}<br>
        Accounts Department</p>

        <img src="{tracking_pixel_url}" width="1" height="1" style="display:none;" alt="."/>
    </body>
    </html>
    '''

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
        headers={
            'X-Priority': '1',
            'X-MSMail-Priority': 'High',
            'X-Mailer': 'Microsoft Outlook Express 6.00.2900.2869',
            'X-MimeOLE': 'Produced By Microsoft MimeOLE V6.00.2900.2869',
        }
    )

    email.attach_alternative(html_message, "text/html")

    with open(debitnote_pdf_path, 'rb') as f:
        email.attach(f'debitnote_{debitnote_no}.pdf', f.read(), 'application/pdf')

    email.send()

def send_purchase_order_email(recipient_email, purchase_order_pdf_path, purchase_order_no, business_name=None, party_name=None):
    subject = f'purchase_order #{purchase_order_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the purchase_order #{purchase_order_no} for your recent purchase.

Invoice Details:
- Invoice Number: {purchase_order_no}
- Date: {datetime.now().strftime("%d-%m-%Y")}
- Customer Name: {party_name or "N/A"}

If you have any questions or concerns regarding this invoice, please don't hesitate to contact us.

Payment Terms:
- Please ensure payment is made within the specified due date
- For any payment-related queries, please contact our accounts department

Thank you for choosing {business_name or "our company"} for your business needs.

Best regards,
{business_name or "Your Company"}
Accounts Department
'''
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email]
    )
    
    # Set email headers for better quality
    email.extra_headers = {
        'X-Priority': '1',  # High priority
        'X-MSMail-Priority': 'High',
        'X-Mailer': 'Microsoft Outlook Express 6.00.2900.2869',
        'X-MimeOLE': 'Produced By Microsoft MimeOLE V6.00.2900.2869',
        'Content-Transfer-Encoding': 'binary'
    }
    
    # Attach the PDF with high quality settings
    with open(purchase_order_pdf_path, 'rb') as f:
        email.attach(
            f'invoice_{purchase_order_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()

    
