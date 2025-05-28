from django.db.models.signals import post_save
from django.dispatch import receiver
from sales.models import Invoice, CreditNote
from purchase.models import Purchase, DebitNote
from .models import DocumentTracking

@receiver(post_save, sender=Invoice)
def create_invoice_tracking(sender, instance, created, **kwargs):
    if created:
        DocumentTracking.objects.create(
            business=instance.business,
            document_type='Invoice',
            invoice=instance
        )

@receiver(post_save, sender=CreditNote)
def create_creditnote_tracking(sender, instance, created, **kwargs):
    if created:
        DocumentTracking.objects.create(
            business=instance.business,
            document_type='CreditNote',
            creditnote=instance
        )

@receiver(post_save, sender=Purchase)
def create_purchase_tracking(sender, instance, created, **kwargs):
    if created:
        DocumentTracking.objects.create(
            business=instance.business,
            document_type='Purchase',
            purchase=instance
        )

@receiver(post_save, sender=DebitNote)
def create_debitnote_tracking(sender, instance, created, **kwargs):
    if created:
        DocumentTracking.objects.create(
            business=instance.business,
            document_type='DebitNote',
            debitnote=instance
        ) 