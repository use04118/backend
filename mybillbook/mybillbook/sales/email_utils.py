# email_utils.py
from django.core.mail import EmailMessage
from django.conf import settings
import os
from datetime import datetime

def send_invoice_email(recipient_email, invoice_pdf_path, invoice_no, business_name=None, party_name=None):
    subject = f'Invoice #{invoice_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{invoice_no} for your recent purchase.

Invoice Details:
- Invoice Number: {invoice_no}
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
    with open(invoice_pdf_path, 'rb') as f:
        email.attach(
            f'invoice_{invoice_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_quotation_email(recipient_email, quotation_pdf_path, quotation_no, business_name=None, party_name=None):
    subject = f'Quotation #{quotation_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{quotation_no} for your recent purchase.

quotation Details:
- quotation Number: {quotation_no}
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
    with open(quotation_pdf_path, 'rb') as f:
        email.attach(
            f'quotation_{quotation_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_payment_in_email(recipient_email, payment_in_pdf_path, payment_in_number, business_name=None, party_name=None):
    subject = f'payment_in #{payment_in_number} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{payment_in_number} for your recent purchase.

Payment In Details:
- Payment In Number: {payment_in_number}
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
    with open(payment_in_pdf_path, 'rb') as f:
        email.attach(
            f'payment_in_{payment_in_number}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_salesreturn_email(recipient_email, salesreturn_pdf_path, salesreturn_no, business_name=None, party_name=None):
    subject = f'salesreturn #{salesreturn_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{salesreturn_no} for your recent purchase.

Invoice Details:
- Invoice Number: {salesreturn_no}
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
    with open(salesreturn_pdf_path, 'rb') as f:
        email.attach(
            f'salesreturn_{salesreturn_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_credit_note_email(recipient_email, credit_note_pdf_path, credit_note_no, business_name=None, party_name=None):
    subject = f'credit_note #{credit_note_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the invoice #{credit_note_no} for your recent purchase.

credit_note Details:
- credit_note Number: {credit_note_no}
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
    with open(credit_note_pdf_path, 'rb') as f:
        email.attach(
            f'credit_note_{credit_note_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_delivery_challan_email(recipient_email, delivery_challan_pdf_path, delivery_challan_no, business_name=None, party_name=None):
    subject = f'delivery_challan #{delivery_challan_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the delivery_challan #{delivery_challan_no} for your recent purchase.

delivery_challan Details:
- delivery_challan Number: {delivery_challan_no}
- Date: {datetime.now().strftime("%d-%m-%Y")}
- Customer Name: {party_name or "N/A"}

If you have any questions or concerns regarding this delivery_challan, please don't hesitate to contact us.

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
    with open(delivery_challan_pdf_path, 'rb') as f:
        email.attach(
            f'delivery_challan_{delivery_challan_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()


def send_proforma_email(recipient_email, proforma_pdf_path, proforma_no, business_name=None, party_name=None):
    subject = f'proforma #{proforma_no} from {business_name or "Your Company"}'
    message = f'''
Dear {party_name or "Valued Customer"},

Thank you for your business with {business_name or "our company"}. Please find attached the proforma #{proforma_no} for your recent purchase.

Invoice Details:
- Invoice Number: {proforma_no}
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
    with open(proforma_pdf_path, 'rb') as f:
        email.attach(
            f'invoice_{proforma_no}.pdf',
            f.read(),
            'application/pdf'
        )
    
    email.send()

    