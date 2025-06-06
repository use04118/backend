
#added manually
from rest_framework import generics
from sales.models import Tcs, Tds
from .models import Purchase,DebitNote,PurchaseReturn,PaymentOut, PurchaseOrder,PaymentOutPurchase
from inventory.models import ItemCategory
from .serializers import PurchaseSerializer,PaymentOutSerializer,PurchaseReturnSerializer,DebitNoteSerializer,PurchaseOrderSerializer, PurchaseItemSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filter import PurchaseFilter
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from django.db.models import Sum
from rest_framework import status
from django.core.cache import cache
from decimal import Decimal
import uuid
from django.http import JsonResponse
from users.utils import get_current_business, log_action
from .permissions import HasPurchasePermission
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
from .email_utils import send_purchase_email, send_purchasereturn_email,send_debitnote_email,send_purchase_order_email,send_payment_out_email
import tempfile
import os
import base64
from django.core.validators import validate_email
from users.models import Business
from parties.models import Party
from datetime import datetime
from django.utils.timezone import now
LOG_FILE = 'invoice_open_logs.txt' # You can change the location if needed


# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated, HasPurchasePermission])  # Assuming you have a purchase permission class
def convert_purchaseorder_to_invoice(request, pk):
    try:
        with transaction.atomic():
            business = get_current_business(request.user)

            # Fetch the purchase order
            purchaseorder = PurchaseOrder.objects.get(id=pk, business=business)

            if purchaseorder.status != 'Open':
                return Response({"error": "Purchase Order must be open to convert to an invoice."},
                                status=status.HTTP_400_BAD_REQUEST)

            # 🔢 Generate next purchase number
            latest_purchase = Purchase.objects.filter(business=business).order_by('-id').first()
            if latest_purchase:
                last_number = int(latest_purchase.purchase_no)
                next_purchase_no = last_number + 1
            else:
                next_purchase_no = 1

            # 📄 Prepare purchase invoice data
            purchase_data = {
                'purchase_no': next_purchase_no,
                'date': purchaseorder.date,
                'party': purchaseorder.party.id,
                'status': 'Unpaid',
                'payment_term': purchaseorder.payment_term,
                'due_date': purchaseorder.due_date,
                'payment_method': 'Cash',
                'bank_account': None,
                'purchase_items': []  # Placeholder
            }

            # 🔐 Serialize and save purchase with business
            purchase_serializer = PurchaseSerializer(data=purchase_data)
            if not purchase_serializer.is_valid():
                return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            purchase = purchase_serializer.save(business=business)

            # 🧾 Add each item from purchase order
            for p_item in purchaseorder.purchaseorder_items.all():
                item_data = {
                    'purchase': purchase.id,
                    'quantity': p_item.quantity,
                    'unit_price': p_item.unit_price,
                    'amount': p_item.amount,
                    'price_item': p_item.price_item,
                }

                if p_item.item:
                    item_data['item'] = p_item.item.id
                    item_data['gstTaxRate'] = p_item.gstTaxRate.id if p_item.gstTaxRate else None
                
                elif p_item.service:
                    item_data['service'] = p_item.service.id
                    item_data['gstTaxRate'] = p_item.gstTaxRate.id if p_item.gstTaxRate else None

                # ✅ Save purchase item
                item_serializer = PurchaseItemSerializer(data=item_data)
                if not item_serializer.is_valid():
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                item_serializer.save()

                # ✅ Increase stock if item
                if p_item.item:
                    p_item.item.closingStock = (p_item.item.closingStock or 0) + p_item.quantity
                    p_item.item.save()

            # ✅ Finalize purchase and purchase order
            purchase.save()
            purchaseorder.status = 'Closed'
            purchaseorder.save()

            return Response({
                "message": "Purchase order successfully converted to purchase invoice.",
                "invoice": PurchaseSerializer(purchase).data
            }, status=status.HTTP_201_CREATED)

    except PurchaseOrder.DoesNotExist:
        return Response({"error": "Purchase Order not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPurchasePermission])
def get_paid(request):
    business = get_current_business(request.user)

    paid_purchase = Purchase.objects.filter(business=business, status='Paid')
    partially_paid_purchase = Purchase.objects.filter(business=business, status='Partially Paid')

    # Sum paid invoice amounts from invoice_items
    total_paid = paid_purchase.aggregate(total=Sum('amount_received'))['total'] or 0
    # Sum only the amount received from partials
    total_partial_paid = partially_paid_purchase.aggregate(total=Sum('amount_received'))['total'] or 0

    total_paid += total_partial_paid

    serialized_purchase = PurchaseSerializer(paid_purchase | partially_paid_purchase, many=True)

    return Response({
        'totalPaid': total_paid,
        'invoices': serialized_purchase.data
    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasPurchasePermission])
def get_unpaid(request):
    business = get_current_business(request.user)

    unpaid_purchase = Purchase.objects.filter(business=business, status='Unpaid')
    partially_paid_purchase = Purchase.objects.filter(business=business, status='Partially Paid')

    # Total from unpaid invoices
    total_unpaid = unpaid_purchase.aggregate(total=Sum('balance_amount'))['total'] or 0
    # Add remaining balance from partials
    total_partial_balance = partially_paid_purchase.aggregate(total=Sum('balance_amount'))['total'] or 0

    total_unpaid += total_partial_balance

    serialized_purchase = PurchaseSerializer(unpaid_purchase | partially_paid_purchase, many=True)

    return Response({
        'totalUnPaid': total_unpaid,
        'invoices': serialized_purchase.data
    }, status=200)



#-------------- PURCHASE INVOICE --------------------------
class PurchaseListCreateView(generics.ListCreateAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return Purchase.objects.filter(business=get_current_business(self.request.user))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        # Get the next purchase number
        next_purchase_no = Purchase.get_next_purchase_number(business)
        # Save the instance with the next purchase number
        instance = serializer.save(business=business, purchase_no=next_purchase_no)
        log_action(self.request.user, business, "purchase_created", {
            "purchase_id": instance.id,
            "purchase_number": instance.purchase_no,
            "amount": float(instance.total_amount) if instance.total_amount else None
        })
        return instance


class PurchaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return Purchase.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "purchase_updated", {
            "purchase_id": instance.id,
            "purchase_number": instance.purchase_no,
            "amount": float(instance.total_amount) if instance.total_amount else None
        })

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "purchase_deleted", {
            "purchase_id": instance.id,
            "purchase_number": instance.purchase_no,
            "amount": float(instance.total_amount) if instance.total_amount else None
        })
        instance.delete()


class PurchaseListView(generics.ListAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    filter_backends = [DjangoFilterBackend]  # Enable filtering
    filterset_class = PurchaseFilter  # Use our custom filter


#----------PAYMENT OUT -------------------------------
class PaymentOutListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentOutSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return PaymentOut.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = PaymentOut.get_next_payment_out_number(business)
        instance = serializer.save(business=business, payment_out_number=next_invoice_no)
        log_action(self.request.user, business, "payment_out_created", {"payment_out_id": instance.id})
        return instance
    
class PaymentOutDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentOutSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return PaymentOut.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "payment_out_updated", {"payment_out_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "payment_out_deleted", {"payment_out_id": instance.id})
        instance.delete()

 #---------- Get Settled Invoices ----------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def settled_purchase(request, payment_out_number):
    try:
        payment = PaymentOut.objects.get(payment_out_number=payment_out_number)
        settled_records = PaymentOutPurchase.objects.filter(payment_out=payment).select_related('purchase')

        settled_purchase = []
        for record in settled_records:
            settled_purchase.append({
                'date': record.purchase.date,
                'purchase_number': record.purchase.purchase_no,
                'purchase_amount': float(record.purchase_amount),
                'purchase_amount_settled': float(record.settled_amount),
                
            })

        return Response({'settled_purchase': settled_purchase}, status=status.HTTP_200_OK)

    except PaymentOut.DoesNotExist:
        return Response({'error': 'PaymentIn not found'}, status=status.HTTP_404_NOT_FOUND)

    
#------------ PURCHASE RETURN------------------------
class PurchaseReturnListCreateView(generics.ListCreateAPIView):
    serializer_class = PurchaseReturnSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return PurchaseReturn.objects.filter(business=get_current_business(self.request.user))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = PurchaseReturn.get_next_purchase_return_number(business)
        instance = serializer.save(business=business,purchasereturn_no=next_invoice_no)
        log_action(self.request.user, business, "purchase_return_created", {"purchase_return_id": instance.id})
        return instance

class PurchaseReturnDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseReturnSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return PurchaseReturn.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "purchase_return_updated", {"purchase_return_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "purchase_return_deleted", {"purchase_return_id": instance.id})
        instance.delete()


#--------------- DEBIT NOTE -----------------------------
class DebitNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = DebitNoteSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return DebitNote.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = DebitNote.get_next_purchase_debit_number(business)
        instance = serializer.save(business=business,debitnote_no=next_invoice_no)
        log_action(self.request.user, business, "debit_note_created", {"debit_note_id": instance.id})
        return instance


class DebitNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DebitNoteSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return DebitNote.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "debit_note_updated", {"debit_note_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "debit_note_deleted", {"debit_note_id": instance.id})
        instance.delete()


# ---------- PURCHASE ORDER  ----------
class PurchaseOrdersListCreateView(generics.ListCreateAPIView):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return PurchaseOrder.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = PurchaseOrder.get_next_purchase_order_number(business)
        instance = serializer.save(business=business,purchase_order_no=next_invoice_no)
        log_action(self.request.user, business, "purchase_order_created", {"purchase_order_id": instance.id})
        return instance
    

class PurchaseOrdersDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated, HasPurchasePermission]

    def get_queryset(self):
        return PurchaseOrder.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "purchase_order_updated", {"purchase_order_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "purchase_order_deleted", {"purchase_order_id": instance.id})
        instance.delete()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_purchase_number(request):
    business = get_current_business(request.user)
    next_invoice_number = Purchase.get_next_purchase_number(business)
    return Response({'next_purchase_number': next_invoice_number})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_payment_out_number(request):
    business = get_current_business(request.user)
    next_invoice_number = PaymentOut.get_next_payment_out_number(business)
    return Response({'next_purchase_out_number': next_invoice_number})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_purchase_return_number(request):
    business = get_current_business(request.user)
    next_invoice_number = PurchaseReturn.get_next_purchase_return_number(business)
    return Response({'next_purchase_return_number': next_invoice_number})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_purchase_debit_number(request):
    business = get_current_business(request.user)
    next_invoice_number = DebitNote.get_next_purchase_debit_number(business)
    return Response({'next_purchase_debit_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_purchase_order_number(request):
    business = get_current_business(request.user)
    next_invoice_number = PurchaseOrder.get_next_purchase_order_number(business)
    return Response({'next_purchase_order_number': next_invoice_number})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_purchase_email_view(request):
    try:
        purchase_no = request.data.get('purchase_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            purchase = Purchase.objects.get(purchase_no=purchase_no, business=business)
            party_name = purchase.party.party_name
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not purchase_no:
            return Response({'error': 'No Purchase number provided'}, status=400)
        
        # Validate email format
        try:
            validate_email(recipient_email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Send the email with business name and party name
            send_purchase_email(recipient_email, temp_file_path, purchase_no, business.name, party_name)
            # Update tracking record
            from tracking.models import DocumentTracking
            tracking = DocumentTracking.objects.get(
                business=business,
                document_type='Purchase',
                purchase=purchase
            )
            tracking.is_sent = True
            tracking.sent_at = now()
            tracking.save()
            
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"{datetime.now().isoformat()} | Purchase | {party_name} | {purchase_no} | email sent to {recipient_email}\n")
            return Response({'message': 'Purchase sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_payment_out_email_view(request):
    try:
        payment_out_number = request.data.get('payment_out_number')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            payment_out = PaymentOut.objects.get(payment_out_number=payment_out_number, business=business)
            party_name = payment_out.party.party_name
        except PaymentOut.DoesNotExist:
            return Response({'error': 'Payment out not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not payment_out_number:
            return Response({'error': 'No Payment out number provided'}, status=400)
        
        # Validate email format
        try:
            validate_email(recipient_email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Send the email with business name and party name
            send_payment_out_email(recipient_email, temp_file_path, payment_out_number, business.name, party_name)
            return Response({'message': 'Payment Out sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_purchasereturn_email_view(request):
    try:
        # print("Received data:", request.data)  # Add this line
        purchasereturn_no = request.data.get('purchasereturn_no')
        # print("Purchase return number:", purchasereturn_no)
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            purchasereturn = PurchaseReturn.objects.get(purchasereturn_no=purchasereturn_no, business=business)
            party_name = purchasereturn.party.party_name
        except PurchaseReturn.DoesNotExist:
            return Response({'error': 'Purchase Return not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not purchasereturn_no:
            return Response({'error': 'No purchasereturn number provided'}, status=400)
        
        # Validate email format
        try:
            validate_email(recipient_email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
            print("------------1------",temp_file_path)
        
        try:
            # Send the email with business name and party name
            send_purchasereturn_email(recipient_email, temp_file_path, purchasereturn_no, business.name, party_name)
            return Response({'message': 'PurchaseReturn sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_debitnote_email_view(request):
    try:
        print("Received data:", request.data)  # Add this line
        debitnote_no = request.data.get('debitnote_no')
        print("debit note number:", debitnote_no)
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            debitnote = DebitNote.objects.get(debitnote_no=debitnote_no, business=business)
            party_name = debitnote.party.party_name
        except DebitNote.DoesNotExist:
            return Response({'error': 'DebitNote not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not debitnote_no:
            return Response({'error': 'No debit note number provided'}, status=400)
        
        # Validate email format
        try:
            validate_email(recipient_email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Send the email with business name and party name
            send_debitnote_email(recipient_email, temp_file_path, debitnote_no, business.name, party_name)
            
            # Update tracking record
            from tracking.models import DocumentTracking
            tracking = DocumentTracking.objects.get(
                business=business,
                document_type='DebitNote',
                debitnote=debitnote
            )
            tracking.is_sent = True
            tracking.sent_at = now()
            tracking.save()
            
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"{datetime.now().isoformat()} | Debit Note | {party_name} | {debitnote_no} | email sent to {recipient_email}\n")
            return Response({'message': 'DebitNote sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_purchase_order_email_view(request):
    try:
        purchase_order_no = request.data.get('purchase_order_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            purchase_order = PurchaseOrder.objects.get(purchase_order_no=purchase_order_no, business=business)
            party_name = purchase_order.party.party_name
        except PurchaseOrder.DoesNotExist:
            return Response({'error': 'purchase_order not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not purchase_order_no:
            return Response({'error': 'No purchase_order number provided'}, status=400)
        
        # Validate email format
        try:
            validate_email(recipient_email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=400)
        
        # Create a temporary file to store the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Send the email with business name and party name
            send_purchase_order_email(recipient_email, temp_file_path, purchase_order_no, business.name, party_name)
            return Response({'message': 'purchase_order sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
       return Response({'error': str(e)}, status=400)