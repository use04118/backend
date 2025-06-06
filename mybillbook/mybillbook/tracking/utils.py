from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive, now
from .models import DocumentTracking
from sales.models import Invoice, CreditNote
from purchase.models import Purchase, DebitNote
from django.core.mail import send_mail
from django.conf import settings

DOCUMENT_MODELS = {
    'Invoice': {
        'model': Invoice,
        'field': 'invoice_no',
        'related_field': 'invoice',
    },
    'CreditNote': {
        'model': CreditNote,
        'field': 'credit_note_no',
        'related_field': 'creditnote',
    },
    'Purchase': {
        'model': Purchase,
        'field': 'purchase_no',
        'related_field': 'purchase',
    },
    'DebitNote': {
        'model': DebitNote,
        'field': 'debitnote_no',
        'related_field': 'debitnote',
    },
}

def update_tracking_from_log(log_path):
    with open(log_path, 'r') as f:
        for line in f:
            try:
                parts = [p.strip() for p in line.strip().split('|')]
                if len(parts) < 4:
                    print(f"⚠️ Skipping malformed line: {line.strip()}")
                    continue

                sent_at_str = parts[0]
                doc_type_raw = parts[1]
                party_name = parts[2]
                doc_no = parts[3]

                sent_at = parse_datetime(sent_at_str)
                if not sent_at:
                    print(f"⚠️ Invalid datetime: {sent_at_str}")
                    continue
                if is_naive(sent_at):
                    sent_at = make_aware(sent_at)

                # Normalize type
                doc_type_key = {
                    'Invoice': 'Invoice',
                    'Credit Note': 'CreditNote',
                    'Purchase': 'Purchase',
                    'Debit Note': 'DebitNote',
                }.get(doc_type_raw)

                if not doc_type_key or doc_type_key not in DOCUMENT_MODELS:
                    print(f"⚠️ Unknown document type '{doc_type_raw}' in line: {line.strip()}")
                    continue

                model_info = DOCUMENT_MODELS[doc_type_key]
                model_class = model_info['model']
                number_field = model_info['field']
                related_field = model_info['related_field']

                # Try by number, then by ID
                doc = model_class.objects.filter(**{number_field: doc_no}).first()
                if not doc and doc_no.isdigit():
                    doc = model_class.objects.filter(id=int(doc_no)).first()

                if not doc:
                    print(f"⚠️ No matching {doc_type_key} found for #{doc_no}")
                    continue

                # Prepare kwargs for one of the four fields
                related_fields = {
                    'invoice': None,
                    'creditnote': None,
                    'purchase': None,
                    'debitnote': None
                }
                related_fields[related_field] = doc

                tracking_obj, created = DocumentTracking.objects.update_or_create(
                    defaults={
                        'is_sent': True,
                        'sent_at': sent_at,
                        'document_type': doc_type_key,
                    },
                    business=doc.business,
                    **related_fields
                )

                print(f"✅ Tracking {'created' if created else 'updated'} for {doc_type_key} #{doc_no}")

            except Exception as e:
                print(f"❌ Error processing line: {line.strip()} (Doc: {doc_type_raw}, #{doc_no})\n{e}")

def send_tracked_email(document_type, document_id, recipient_email, subject, message):
    """
    Send an email with tracking pixel and update tracking record
    """
    try:
        # Get the tracking record
        tracking = None
        if document_type == 'Invoice':
            tracking = DocumentTracking.objects.get(invoice__id=document_id)
        elif document_type == 'CreditNote':
            tracking = DocumentTracking.objects.get(creditnote__id=document_id)
        elif document_type == 'Purchase':
            tracking = DocumentTracking.objects.get(purchase__id=document_id)
        elif document_type == 'DebitNote':
            tracking = DocumentTracking.objects.get(debitnote__id=document_id)

        if tracking:
            # Add tracking pixel to email
            tracking_url = f"{settings.BASE_URL}/track-email-open/?doc_type={document_type}&doc_id={document_id}"
            tracking_pixel = f'<img src="{tracking_url}" width="1" height="1" />'
            message_with_tracking = f"{message}\n\n{tracking_pixel}"

            # Send email
            send_mail(
                subject=subject,
                message=message_with_tracking,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=message_with_tracking
            )

            # Update tracking record
            tracking.is_sent = True
            tracking.sent_at = now()
            tracking.save()

            return True
    except DocumentTracking.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error sending tracked email: {str(e)}")
        return False