from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

from sales.models import Invoice,CreditNote
from purchase.models import Purchase, DebitNote
from users.models import Business

User = get_user_model()

class DocumentTracking(models.Model):
    DOCUMENT_TYPE_CHOICES = [
    ('Invoice', 'Invoice'),
    ('CreditNote', 'Credit Note'),
    ('Purchase', 'Purchase'),
    ('DebitNote', 'Debit Note'),
]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='tracking')
    # Only one of these should be non-null for each entry
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, blank=True, related_name='tracking')
    creditnote = models.ForeignKey(CreditNote, on_delete=models.CASCADE, null=True, blank=True, related_name='tracking')
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null=True, blank=True, related_name='tracking')
    debitnote = models.ForeignKey(DebitNote, on_delete=models.CASCADE, null=True, blank=True, related_name='tracking')
    

    is_sent = models.BooleanField(default=False)
    is_opened = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def document_number(self):
        try:
            if self.document_type == 'Invoice' and self.invoice:
                return self.invoice.invoice_no
            elif self.document_type == 'CreditNote' and self.creditnote:
                return self.creditnote.credit_note_no
            elif self.document_type == 'Purchase' and self.purchase:
                return self.purchase.purchase_no
            elif self.document_type == 'DebitNote' and self.debitnote:
                return self.debitnote.debitnote_no
            elif self.document_type == 'Quotation' and self.quotation:
                return self.quotation.quotation_no
            elif self.document_type == 'Purchase Return' and self.purchase_return:
                return self.purchase_return.purchase_return_no
            elif self.document_type == 'Sales Return' and self.sales_return:
                return self.sales_return.sales_return_no
            return 'N/A'
        except:
            return 'N/A'

    def __str__(self):
        status = 'Opened' if self.is_opened else 'Unopened'
        return f"{self.document_type} - {self.document_number()} ({status})"

