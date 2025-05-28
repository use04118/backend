

# Register your models here.
from django.contrib import admin
from .models import DocumentTracking

@admin.register(DocumentTracking)
class DocumentTrackingAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'document_number', 'business', 'is_sent', 'is_opened', 'sent_at', 'opened_at']
    list_filter = ['document_type', 'is_opened']
