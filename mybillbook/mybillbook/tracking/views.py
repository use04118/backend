# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import DocumentTracking
from .serializers import DocumentTrackingSerializer
from django.http import HttpResponse
from django.utils.timezone import now
from users.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tracking_list_view(request):
    business = request.user.current_business
    
    # Get all tracking records for the business
    trackings = DocumentTracking.objects.filter(business=business).order_by('-created_at')
    
    # Prepare the response data
    tracking_data = []
    for tracking in trackings:
        # Get document details based on document type
        if tracking.document_type == 'Invoice' and tracking.invoice:
            doc = tracking.invoice
            party_name = doc.party.party_name if doc.party else 'N/A'
            total_amount = doc.total_amount
        elif tracking.document_type == 'CreditNote' and tracking.creditnote:
            doc = tracking.creditnote
            party_name = doc.party.party_name if doc.party else 'N/A'
            total_amount = doc.total_amount
        elif tracking.document_type == 'Purchase' and tracking.purchase:
            doc = tracking.purchase
            party_name = doc.party.party_name if doc.party else 'N/A'
            total_amount = doc.total_amount
        elif tracking.document_type == 'DebitNote' and tracking.debitnote:
            doc = tracking.debitnote
            party_name = doc.party.party_name if doc.party else 'N/A'
            total_amount = doc.total_amount
        else:
            continue

        tracking_data.append({
            'id': tracking.id,
            'document_number': tracking.document_number(),
            'created_at': tracking.created_at,
            'party_name': party_name,
            'total_amount': total_amount,
            'document_type': tracking.document_type,
            'is_sent': tracking.is_sent,
            'is_opened': tracking.is_opened,
            'sent_at': tracking.sent_at,
            'opened_at': tracking.opened_at
        })

    return Response(tracking_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_document_tracking(request):
    business = request.user.current_business
    doc_type = request.GET.get('document_type')
    doc_id = request.GET.get('invoice')  # or creditnote, purchase, debitnote

    filters = {'business': business}
    if doc_type:
        filters['document_type'] = doc_type
    if doc_id:
        if doc_type == 'Invoice':
            filters['invoice__id'] = doc_id
        elif doc_type == 'CreditNote':
            filters['creditnote__id'] = doc_id
        elif doc_type == 'Purchase':
            filters['purchase__id'] = doc_id
        elif doc_type == 'DebitNote':
            filters['debitnote__id'] = doc_id

    trackings = DocumentTracking.objects.filter(**filters).order_by('-created_at')
    serializer = DocumentTrackingSerializer(trackings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def track_email_open(request):
    doc_type = request.GET.get('doc_type')
    doc_id = request.GET.get('doc_id')

    try:
        tracking = None

        if doc_type == 'Invoice':
            tracking = DocumentTracking.objects.get(invoice__id=doc_id)
        elif doc_type == 'CreditNote':
            tracking = DocumentTracking.objects.get(creditnote__id=doc_id)
        elif doc_type == 'Purchase':
            tracking = DocumentTracking.objects.get(purchase__id=doc_id)
        elif doc_type == 'DebitNote':
            tracking = DocumentTracking.objects.get(debitnote__id=doc_id)

        if tracking and not tracking.is_opened:
            tracking.is_opened = True
            tracking.opened_at = now()
            tracking.save()
    except DocumentTracking.DoesNotExist:
        pass  # optionally log this

    # Return a 1x1 transparent PNG
    transparent_pixel = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\xff\x00\xc0\xc0'
        b'\xc0\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00'
        b'\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    )
    return HttpResponse(transparent_pixel, content_type='image/gif')