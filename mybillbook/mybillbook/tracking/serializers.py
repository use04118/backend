# serializers.py
from rest_framework import serializers
from .models import DocumentTracking

class DocumentTrackingSerializer(serializers.ModelSerializer):
    document_number = serializers.SerializerMethodField()

    class Meta:
        model = DocumentTracking
        fields = [
            'id', 'business', 'document_type', 'invoice', 'creditnote', 'purchase', 'debitnote',
            'is_sent', 'is_opened', 'sent_at', 'opened_at', 'created_at', 'document_number'
        ]
        read_only_fields = ['created_at', 'document_number']

    def get_document_number(self, obj):
        return obj.document_number()