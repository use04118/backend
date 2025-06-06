from django.http import JsonResponse
#added manually
from rest_framework import generics
from .models import Invoice, Quotation, Proforma, DeliveryChallan,PaymentIn,SalesReturn,CreditNote,PaymentInInvoice
from .serializers import InvoiceSerializer, QuotationSerializer, ProformaSerializer, DeliveryChallanSerializer,PaymentInSerializer,SalesReturnSerializer,CreditNoteSerializer,InvoiceItemSerializer
from rest_framework.exceptions import ValidationError
#for gstin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from inventory.models import Item
import uuid
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.utils import get_current_business, log_action
from .permissions import HasSalesPermission
from .models import Tcs, Tds
from .serializers import TcsSerializer, TdsSerializer
from rest_framework import serializers
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .email_utils import send_invoice_email, send_quotation_email,send_salesreturn_email,send_credit_note_email,send_delivery_challan_email,send_proforma_email,send_payment_in_email
import tempfile
import os
import base64
from django.core.validators import validate_email
from datetime import datetime
from django.utils.timezone import now
LOG_FILE = 'invoice_open_logs.txt' # You can change the location if needed

# List & Create TCS
class TcsListCreateView(generics.ListCreateAPIView):
    serializer_class = TcsSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        business = get_current_business(self.request.user)
        return Tcs.objects.filter(Q(business=None) | Q(business=business))


    def create(self, request, *args, **kwargs):
        business = get_current_business(request.user)
        data = request.data
        is_bulk = isinstance(data, list)

        serializer = self.get_serializer(data=data, many=is_bulk)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer, business, is_bulk)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer, business, is_bulk):
        if self.request.user.is_superuser:
            # Superuser can post global rates
            instances = serializer.save(business=None)
        else:
            instances = serializer.save(business=business)
        if is_bulk:
            for tcs in instances:
                log_action(self.request.user, business, "tcs_created", {"rate": str(tcs.rate), "description": tcs.description})
        else:
            tcs = instances
            log_action(self.request.user, business, "tcs_created", {"rate": str(tcs.rate), "description": tcs.description})

# Update/Delete TCS
class TcsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TcsSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Tcs.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        tcs = serializer.save()
        log_action(self.request.user, get_current_business(self.request.user), "tcs_updated", {"rate": str(tcs.rate)})

    def perform_destroy(self, instance):
        log_action(self.request.user, get_current_business(self.request.user), "tcs_deleted", {"rate": str(instance.rate)})
        instance.delete()

# List & Create TDS
class TdsListCreateView(generics.ListCreateAPIView):
    serializer_class = TdsSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        business = get_current_business(self.request.user)
        return Tds.objects.filter(Q(business=None) | Q(business=business))


    def create(self, request, *args, **kwargs):
        business = get_current_business(request.user)
        data = request.data
        is_bulk = isinstance(data, list)

        serializer = self.get_serializer(data=data, many=is_bulk)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer, business, is_bulk)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer, business, is_bulk):
        if self.request.user.is_superuser:
            # Superuser can post global rates
            instances = serializer.save(business=None)
        else:
            instances = serializer.save(business=business)
        if is_bulk:
            for tds in instances:
                log_action(self.request.user, business, "tds_created", {"rate": str(tds.rate), "description": tds.description})
        else:
            tds = instances
            log_action(self.request.user, business, "tds_created", {"rate": str(tds.rate), "description": tds.description})

# Update/Delete TDS
class TdsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TdsSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Tds.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        tds = serializer.save()
        log_action(self.request.user, get_current_business(self.request.user), "tds_updated", {"rate": str(tds.rate)})

    def perform_destroy(self, instance):
        log_action(self.request.user, get_current_business(self.request.user), "tds_deleted", {"rate": str(instance.rate)})
        instance.delete()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def business_tax_flags(request):
    business = get_current_business(request.user)
    signature = None
    if business.signature and hasattr(business.signature, 'file'):
        try:
            # Read the image file content
            with business.signature.open('rb') as image_file:
                signature = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error processing signature: {str(e)}")
            signature = None
    
    return Response({
        "tcs": business.tcs,
        "tds": business.tds,
        "state": business.state,
        "signature": signature,
        "business_name":business.name,
        "business_phone":business.phone,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasSalesPermission])
def list_items(request):
    items = Item.objects.all()
    data = []
    for item in items:
        data.append({
            'item_name': item.itemName,
            'description': item.description,
            'available_stock': item.closingStock,  # Show the available stock
            'sales_price': item.salesPrice,
        })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasSalesPermission])
def convert_quotation_to_invoice(request, pk):
    try:
        with transaction.atomic():
            business = get_current_business(request.user)

            # Fetch the quotation
            quotation = Quotation.objects.get(id=pk, business=business)

            if quotation.status != 'Open':
                return Response({"error": "Quotation must be open to convert to an invoice."},
                                status=status.HTTP_400_BAD_REQUEST)

            # 🔢 Generate next invoice number for this business
            latest_invoice = Invoice.objects.filter(business=business).order_by('-id').first()
            if latest_invoice:
                # Extract the number part and increment
                last_number = int(latest_invoice.invoice_no)
                next_invoice_no = last_number + 1
            else:
                # First invoice for this business
                next_invoice_no = 1


            # 📄 Prepare invoice data
            invoice_data = {
                'invoice_no': next_invoice_no,
                'date': quotation.date,
                'party': quotation.party.id,
                'status': 'Unpaid',
                'payment_term': quotation.payment_term,
                'due_date': quotation.due_date,
                'amount_received': 0,
                'is_fully_paid': False,
                'payment_method': 'Cash',
                'bank_account': None,
                'invoice_items': []  # Placeholder
            }

            # 🔐 Serialize and save invoice with business
            invoice_serializer = InvoiceSerializer(data=invoice_data)
            if not invoice_serializer.is_valid():
                return Response(invoice_serializer.errors, status=400)

            invoice = invoice_serializer.save(business=business)  # ✅ Inject business here

            # 🧾 Add each item from quotation
            for q_item in quotation.quotation_items.all():
                item_data = {
                    'invoice': invoice.id,
                    'quantity': q_item.quantity,
                    'unit_price': q_item.unit_price,
                    'amount': q_item.amount,
                    'price_item': q_item.price_item,
                    'discount': q_item.discount,
                }

                if q_item.item:
                    item_data['item'] = q_item.item.id
                    item_data['gstTaxRate'] = q_item.gstTaxRate.id if q_item.gstTaxRate else None
                elif q_item.service:
                    item_data['service'] = q_item.service.id
                    item_data['gstTaxRate'] = q_item.gstTaxRate.id if q_item.gstTaxRate else None

                # ✅ Save invoice item
                item_serializer = InvoiceItemSerializer(data=item_data)
                if not item_serializer.is_valid():
                    return Response(item_serializer.errors, status=400)

                item_serializer.save()

                # ✅ Reduce stock if item
                if q_item.item:
                    stock = q_item.item.closingStock or 0
                    if stock < q_item.quantity:
                        return Response({
                            "error": f"Not enough stock for {q_item.item.itemName}. "
                                     f"Available: {stock}, Required: {q_item.quantity}"
                        }, status=400)
                    q_item.item.closingStock -= q_item.quantity
                    q_item.item.save()

            # ✅ Finalize invoice and quotation
            invoice.save()
            quotation.status = 'Closed'
            quotation.save()

            return Response({
                "message": "Quotation successfully converted to invoice.",
                "invoice": InvoiceSerializer(invoice).data
            }, status=201)

    except Quotation.DoesNotExist:
        return Response({"error": "Quotation not found."}, status=404)
    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasSalesPermission])
def convert_deliverychallan_to_invoice(request, pk):
    try:
        with transaction.atomic():
            business = get_current_business(request.user)

            # Get delivery challan
            deliverychallan = DeliveryChallan.objects.get(id=pk, business=business)

            if deliverychallan.status != 'Open':
                return Response(
                    {"error": "Delivery Challan must be open to convert to an invoice."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate invoice number
            latest_invoice = Invoice.objects.filter(business=business).order_by('-id').first()
            if latest_invoice:
                # Extract the number part and increment
                last_number = int(latest_invoice.invoice_no)
                next_invoice_no = last_number + 1
            else:
                # First invoice for this business
                next_invoice_no = 1

            # Prepare invoice data
            invoice_data = {
                'invoice_no': next_invoice_no,
                'date': deliverychallan.date,
                'party': deliverychallan.party.id,
                'status': 'Unpaid',
                'payment_term': deliverychallan.payment_term,
                'due_date': deliverychallan.due_date,
                'amount_received': 0,
                'is_fully_paid': False,
                'payment_method': 'Cash',
                'bank_account': None,
                'invoice_items': []  # Will populate below
            }

            # Create invoice
            invoice_serializer = InvoiceSerializer(data=invoice_data)
            if not invoice_serializer.is_valid():
                return Response(invoice_serializer.errors, status=400)

            invoice = invoice_serializer.save(business=business)

            # Add deliverychallan items to invoice
            for dc_item in deliverychallan.deliverychallan_items.all():
                item_data = {
                    'invoice': invoice.id,
                    'quantity': dc_item.quantity,
                    'unit_price': dc_item.unit_price,
                    'amount': dc_item.amount,
                    'price_item': dc_item.price_item,
                    'discount': dc_item.discount,
                }

                if dc_item.item:
                    item_data['item'] = dc_item.item.id
                    item_data['gstTaxRate'] = dc_item.gstTaxRate.id if dc_item.gstTaxRate else None
                elif dc_item.service:
                    item_data['service'] = dc_item.service.id
                    item_data['gstTaxRate'] = dc_item.gstTaxRate.id if dc_item.gstTaxRate else None
                else:
                    continue

                # Save invoice item
                item_serializer = InvoiceItemSerializer(data=item_data)
                if not item_serializer.is_valid():
                    return Response(item_serializer.errors, status=400)

                item_serializer.save()

                # Deduct stock if item
                if dc_item.item:
                    stock = dc_item.item.closingStock or 0
                    if stock < dc_item.quantity:
                        return Response({
                            "error": f"Not enough stock for {dc_item.item.itemName}. "
                                     f"Available: {stock}, Required: {dc_item.quantity}"
                        }, status=400)
                    dc_item.item.closingStock -= dc_item.quantity
                    dc_item.item.save()

            # Finalize invoice and close challan
            invoice.save()
            deliverychallan.status = 'Closed'
            deliverychallan.save()

            return Response({
                "message": "Delivery Challan successfully converted to invoice.",
                "invoice": InvoiceSerializer(invoice).data
            }, status=201)

    except DeliveryChallan.DoesNotExist:
        return Response({"error": "Delivery Challan not found."}, status=404)

    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasSalesPermission])
def convert_proforma_to_invoice(request, pk):
    try:
        with transaction.atomic():
            business = get_current_business(request.user)

            # Get the proforma invoice within the current business
            proforma = Proforma.objects.get(id=pk, business=business)

            if proforma.status != 'Open':
                return Response(
                    {"error": "Proforma must be open to convert to an invoice."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate invoice number
            latest_invoice = Invoice.objects.filter(business=business).order_by('-id').first()
            if latest_invoice:
                # Extract the number part and increment
                last_number = int(latest_invoice.invoice_no)
                next_invoice_no = last_number + 1
            else:
                # First invoice for this business
                next_invoice_no = 1

            # Prepare invoice data
            invoice_data = {
                'invoice_no': next_invoice_no,
                'date': proforma.date,
                'party': proforma.party.id,
                'status': 'Unpaid',
                'payment_term': proforma.payment_term,
                'due_date': proforma.due_date,
                'amount_received': 0,
                'is_fully_paid': False,
                'payment_method': 'Cash',
                'bank_account': None,
                'invoice_items': []  # Will be populated below
            }

            invoice_serializer = InvoiceSerializer(data=invoice_data)
            if not invoice_serializer.is_valid():
                return Response(invoice_serializer.errors, status=400)

            invoice = invoice_serializer.save(business=business)

            # Add each item to invoice
            for p_item in proforma.proforma_items.all():
                item_data = {
                    'invoice': invoice.id,
                    'quantity': p_item.quantity,
                    'unit_price': p_item.unit_price,
                    'amount': p_item.amount,
                    'price_item': p_item.price_item,
                    'discount': p_item.discount,
                }

                if p_item.item:
                    item_data['item'] = p_item.item.id
                    item_data['gstTaxRate'] = p_item.gstTaxRate.id if p_item.gstTaxRate else None
                elif p_item.service:
                    item_data['service'] = p_item.service.id
                    item_data['gstTaxRate'] = p_item.gstTaxRate.id if p_item.gstTaxRate else None
                else:
                    continue

                item_serializer = InvoiceItemSerializer(data=item_data)
                if not item_serializer.is_valid():
                    return Response(item_serializer.errors, status=400)

                item_serializer.save()

                # Deduct stock if item
                if p_item.item:
                    stock = p_item.item.closingStock or 0
                    if stock < p_item.quantity:
                        return Response({
                            "error": f"Not enough stock for {p_item.item.itemName}. "
                                     f"Available: {stock}, Required: {p_item.quantity}"
                        }, status=400)
                    p_item.item.closingStock -= p_item.quantity
                    p_item.item.save()

            # Finalize invoice and close proforma
            invoice.save()
            proforma.status = 'Closed'
            proforma.save()

            return Response({
                "message": "Proforma successfully converted to invoice.",
                "invoice": InvoiceSerializer(invoice).data
            }, status=201)

    except Proforma.DoesNotExist:
        return Response({"error": "Proforma not found."}, status=404)

    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasSalesPermission])
def get_paid(request):
    business = get_current_business(request.user)

    paid_invoices = Invoice.objects.filter(business=business, status='Paid')
    partially_paid_invoices = Invoice.objects.filter(business=business, status='Partially Paid')

    # Sum paid invoice amounts from invoice_items
    total_paid = paid_invoices.aggregate(total=Sum('amount_received'))['total'] or 0
    # Sum only the amount received from partials
    total_partial_paid = partially_paid_invoices.aggregate(total=Sum('amount_received'))['total'] or 0

    total_paid += total_partial_paid

    serialized_invoices = InvoiceSerializer(paid_invoices | partially_paid_invoices, many=True)

    return Response({
        'totalPaid': total_paid,
        'invoices': serialized_invoices.data
    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated, HasSalesPermission])
def get_unpaid(request):
    business = get_current_business(request.user)

    unpaid_invoices = Invoice.objects.filter(business=business, status='Unpaid')
    partially_paid_invoices = Invoice.objects.filter(business=business, status='Partially Paid')

    # Total from unpaid invoices
    total_unpaid = unpaid_invoices.aggregate(total=Sum('balance_amount'))['total'] or 0
    # Add remaining balance from partials
    total_partial_balance = partially_paid_invoices.aggregate(total=Sum('balance_amount'))['total'] or 0

    total_unpaid += total_partial_balance

    serialized_invoices = InvoiceSerializer(unpaid_invoices | partially_paid_invoices, many=True)

    return Response({
        'totalUnPaid': total_unpaid,
        'invoices': serialized_invoices.data
    }, status=200)


# ---------- INVOICE ----------
class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Invoice.objects.filter(business=get_current_business(self.request.user))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        # Get the next invoice number
        next_invoice_no = Invoice.get_next_invoice_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, invoice_no=next_invoice_no)
        log_action(self.request.user, business, "invoice_created", {
            "invoice_id": instance.id,
            "invoice_number": instance.invoice_no,
            "amount": float(instance.total_amount) if instance.total_amount else None
        })
        return instance


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Invoice.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "invoice_updated", {
            "invoice_id": instance.id,
            "invoice_number": instance.invoice_no,
            "amount": float(instance.total_amount) if instance.total_amount else None
        })

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "invoice_deleted", {
            "invoice_id": instance.id,
            "invoice_number": instance.invoice_no,
            "amount": float(instance.total_amount) if instance.total_amount else None
        })
        instance.delete()


# ---------- QUOTATION ----------
class QuotationListCreateView(generics.ListCreateAPIView):
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Quotation.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = Quotation.get_next_quotation_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, quotation_no=next_invoice_no)
    
        log_action(self.request.user, business, "quotation_created", {"quotation_id": instance.id})
        return instance


class QuotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuotationSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Quotation.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "quotation_updated", {"quotation_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "quotation_deleted", {"quotation_id": instance.id})
        instance.delete()

# ---------- PAYMENT IN ----------
class PaymentInListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentInSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return PaymentIn.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = PaymentIn.get_next_payment_in_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, payment_in_number=next_invoice_no)
        log_action(self.request.user, business, "payment_in_created", {"payment_in_id": instance.id})
        return instance


class PaymentInDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentInSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return PaymentIn.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "payment_in_updated", {"payment_in_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "payment_in_deleted", {"payment_in_id": instance.id})
        instance.delete()


# ---------- Get Settled Invoices ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def settled_invoices(request, payment_in_number):
    try:
        payment = PaymentIn.objects.get(payment_in_number=payment_in_number)
        settled_records = PaymentInInvoice.objects.filter(payment_in=payment).select_related('invoice')

        settled_invoices = []
        for record in settled_records:
            settled_invoices.append({
                'date': record.invoice.date,
                'invoice_number': record.invoice.invoice_no,
                'invoice_amount': float(record.invoice_amount),
                'invoice_amount_settled': float(record.settled_amount),
                'invoice_tds_amount': float(record.tds_amount),
            })

        return Response({'settled_invoices': settled_invoices}, status=status.HTTP_200_OK)

    except PaymentIn.DoesNotExist:
        return Response({'error': 'PaymentIn not found'}, status=status.HTTP_404_NOT_FOUND)

    
# ---------- SALES RETURN ----------
class SalesReturnListCreateView(generics.ListCreateAPIView):
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return SalesReturn.objects.filter(business=get_current_business(self.request.user))
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = SalesReturn.get_next_salesreturn_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, salesreturn_no=next_invoice_no)
        log_action(self.request.user, business, "sales_return_created", {"sales_return_id": instance.id})
        return instance


class SalesReturnDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SalesReturnSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return SalesReturn.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "sales_return_updated", {"sales_return_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "sales_return_deleted", {"sales_return_id": instance.id})
        instance.delete()


# ---------- CREDIT NOTE ----------
class CreditNoteListCreateView(generics.ListCreateAPIView):
    serializer_class = CreditNoteSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return CreditNote.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = CreditNote.get_next_creditnote_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, credit_note_no=next_invoice_no)
        log_action(self.request.user, business, "credit_note_created", {"credit_note_id": instance.id})
        return instance


class CreditNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreditNoteSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return CreditNote.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "credit_note_updated", {"credit_note_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "credit_note_deleted", {"credit_note_id": instance.id})
        instance.delete()


# ---------- DELIVERY CHALLAN ----------
class DeliveryChallanListCreateView(generics.ListCreateAPIView):
    serializer_class = DeliveryChallanSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return DeliveryChallan.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
        next_invoice_no = DeliveryChallan.get_next_deliverychallan_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, delivery_challan_no=next_invoice_no)
        log_action(self.request.user, business, "delivery_challan_created", {"delivery_challan_id": instance.id})
        return instance


class DeliveryChallanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DeliveryChallanSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return DeliveryChallan.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "delivery_challan_updated", {"delivery_challan_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "delivery_challan_deleted", {"delivery_challan_id": instance.id})
        instance.delete()


# ---------- PROFORMA ----------
class ProformaListCreateView(generics.ListCreateAPIView):
    serializer_class = ProformaSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Proforma.objects.filter(business=get_current_business(self.request.user))

    def perform_create(self, serializer):
        business = get_current_business(self.request.user)
       
        next_invoice_no = Proforma.get_next_proforma_number(business)
        # Save the instance with the next invoice number
        instance = serializer.save(business=business, proforma_no=next_invoice_no)
    
        log_action(self.request.user, business, "proforma_created", {"proforma_id": instance.id})
        return instance


class ProformaDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProformaSerializer
    permission_classes = [IsAuthenticated, HasSalesPermission]

    def get_queryset(self):
        return Proforma.objects.filter(business=get_current_business(self.request.user))

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, instance.business, "proforma_updated", {"proforma_id": instance.id})

    def perform_destroy(self, instance):
        log_action(self.request.user, instance.business, "proforma_deleted", {"proforma_id": instance.id})
        instance.delete()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_invoice_number(request):
    business = get_current_business(request.user)
    next_invoice_number = Invoice.get_next_invoice_number(business)
    return Response({'next_invoice_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_quotation_number(request):
    business = get_current_business(request.user)
    next_invoice_number = Quotation.get_next_quotation_number(business)
    return Response({'next_quotation_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_payment_in_number(request):
    business = get_current_business(request.user)
    next_invoice_number = PaymentIn.get_next_payment_in_number(business)
    return Response({'next_payment_in_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_salesreturn_number(request):
    business = get_current_business(request.user)
    next_invoice_number = SalesReturn.get_next_salesreturn_number(business)
    return Response({'next_salesreturn_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_creditnote_number(request):
    business = get_current_business(request.user)
    next_invoice_number = CreditNote.get_next_creditnote_number(business)
    return Response({'next_creditnote_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_deliverychallan_number(request):
    business = get_current_business(request.user)
    next_invoice_number = DeliveryChallan.get_next_deliverychallan_number(business)
    return Response({'next_deliverychallan_number': next_invoice_number})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_next_proforma_number(request):
    business = get_current_business(request.user)
    next_invoice_number = Proforma.get_next_proforma_number(business)
    return Response({'next_proforma_number': next_invoice_number})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_invoice_email_view(request):
    try:
        invoice_no = request.data.get('invoice_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            invoice = Invoice.objects.get(invoice_no=invoice_no, business=business)
            party_name = invoice.party.party_name
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not invoice_no:
            return Response({'error': 'No invoice number provided'}, status=400)
        
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
            send_invoice_email(recipient_email, temp_file_path, invoice_no, invoice.id, business.name, party_name)
            
            # Update tracking record
            from tracking.models import DocumentTracking
            tracking = DocumentTracking.objects.get(
                business=business,
                document_type='Invoice',
                invoice=invoice
            )
            tracking.is_sent = True
            tracking.sent_at = now()
            tracking.save()
            
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"{datetime.now().isoformat()} | Invoice | {party_name} | {invoice_no} | email sent to {recipient_email}\n")
            return Response({'message': 'Invoice sent successfully'})
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_quotation_email_view(request):
    try:
        quotation_no = request.data.get('quotation_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            quotation = Quotation.objects.get(quotation_no=quotation_no, business=business)
            party_name = quotation.party.party_name
        except Quotation.DoesNotExist:
            return Response({'error': 'Quotation not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not quotation_no:
            return Response({'error': 'No quotation number provided'}, status=400)
        
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
            send_quotation_email(recipient_email, temp_file_path, quotation_no, business.name, party_name)
            return Response({'message': 'Quotation sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_payment_in_email_view(request):
    try:
        payment_in_number = request.data.get('payment_in_number')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            payment_in = PaymentIn.objects.get(payment_in_number=payment_in_number, business=business)
            party_name = payment_in.party.party_name
        except PaymentIn.DoesNotExist:
            return Response({'error': 'Payment out not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not payment_in_number:
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
            send_payment_in_email(recipient_email, temp_file_path, payment_in_number, business.name, party_name)
            return Response({'message': 'Payment Out sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_salesreturn_email_view(request):
    try:
        salesreturn_no = request.data.get('salesreturn_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            salesreturn = SalesReturn.objects.get(salesreturn_no=salesreturn_no, business=business)
            party_name = salesreturn.party.party_name
        except SalesReturn.DoesNotExist:
            return Response({'error': 'SalesReturn not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not salesreturn_no:
            return Response({'error': 'No salesreturn number provided'}, status=400)
        
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
            send_salesreturn_email(recipient_email, temp_file_path, salesreturn_no, business.name, party_name)
            return Response({'message': 'SalesReturn sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_credit_note_email_view(request):
    try:
        credit_note_no = request.data.get('credit_note_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            credit_note = CreditNote.objects.get(credit_note_no=credit_note_no, business=business)
            party_name = credit_note.party.party_name
        except CreditNote.DoesNotExist:
            return Response({'error': 'CreditNote not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not credit_note_no:
            return Response({'error': 'No credit_note number provided'}, status=400)
        
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
            send_credit_note_email(recipient_email, temp_file_path, credit_note_no, business.name, party_name)
            # Update tracking record
            from tracking.models import DocumentTracking
            tracking = DocumentTracking.objects.get(
                business=business,
                document_type='CreditNote',
                creditnote=credit_note
            )
            tracking.is_sent = True
            tracking.sent_at = now()
            tracking.save()
            
            with open(LOG_FILE, 'a') as log_file:
                log_file.write(f"{datetime.now().isoformat()} | Credit Note | {party_name} | {credit_note_no} | email sent to {recipient_email}\n")
            return Response({'message': 'CreditNote sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_deliverychallan_email_view(request):
    try:
        delivery_challan_no = request.data.get('delivery_challan_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            delivery_challan = DeliveryChallan.objects.get(delivery_challan_no=delivery_challan_no, business=business)
            party_name = delivery_challan.party.party_name
        except DeliveryChallan.DoesNotExist:
            return Response({'error': 'DeliveryChallan not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not delivery_challan_no:
            return Response({'error': 'No deliverychallan number provided'}, status=400)
        
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
            send_delivery_challan_email(recipient_email, temp_file_path, delivery_challan_no, business.name, party_name)
            return Response({'message': 'DeliveryChallan sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        return Response({'error': str(e)}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_proforma_email_view(request):
    try:
        proforma_no = request.data.get('proforma_no')
        recipient_email = request.data.get('email')
        pdf_file = request.FILES.get('pdf_file')
        business = get_current_business(request.user)
        
        # Get the invoice to find the party name
        try:
            proforma = Proforma.objects.get(proforma_no=proforma_no, business=business)
            party_name = proforma.party.party_name
        except Proforma.DoesNotExist:
            return Response({'error': 'Proforma not found'}, status=404)
        
        if not pdf_file:
            return Response({'error': 'No PDF file provided'}, status=400)
        
        if not recipient_email:
            return Response({'error': 'No recipient email provided'}, status=400)
            
        if not proforma_no:
            return Response({'error': 'No proforma number provided'}, status=400)
        
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
            send_proforma_email(recipient_email, temp_file_path, proforma_no, business.name, party_name)
            return Response({'message': 'Proforma sent successfully'})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
       return Response({'error': str(e)}, status=400)