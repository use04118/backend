# management/commands/update_sent_status.py

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from tracking.models import DocumentTracking
from sales.models import Invoice, CreditNote
from purchase.models import Purchase, DebitNote

LOG_FILE = 'invoice_open_logs.txt'  # Update path if needed

DOCUMENT_MODELS = {
    'Invoice': Invoice,
    'CreditNote': CreditNote,
    'Purchase': Purchase,
    'DebitNote': DebitNote,
}

class Command(BaseCommand):
    help = 'Update DocumentTracking from invoice_open_logs.txt'

    def handle(self, *args, **kwargs):
        with open(LOG_FILE, 'r') as log_file:
            for line in log_file:
                try:
                    parts = line.strip().split('|')
                    sent_at = parse_datetime(parts[0].strip())
                    doc_no = parts[2].strip()
                    email_info = parts[3].strip()

                    # Detect document type by matching doc number
                    for doc_type, model in DOCUMENT_MODELS.items():
                        lookup_field = {
                            'Invoice': 'invoice_no',
                            'CreditNote': 'credit_note_no',
                            'Purchase': 'purchase_no',
                            'DebitNote': 'debit_note_no'
                        }.get(doc_type, 'invoice_no')

                        doc = model.objects.filter(**{lookup_field: doc_no}).first()
                        if doc:
                            # Update or create DocumentTracking
                            tracking_filter = {doc_type.lower(): doc}
                            DocumentTracking.objects.update_or_create(
                                **tracking_filter,
                                defaults={
                                    'document_type': doc_type,
                                    'is_sent': True,
                                    'sent_at': sent_at,
                                }
                            )
                            break
                except Exception as e:
                    self.stderr.write(f"Error processing line: {line}\n{e}")
