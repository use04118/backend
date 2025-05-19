from django.http import JsonResponse
from django.db.models import Value, CharField,F, Sum, Count, Q
from sales.models import Invoice, Quotation, SalesReturn, CreditNote, PaymentIn, DeliveryChallan,Proforma
from purchase.models import Purchase, PurchaseReturn, DebitNote, PaymentOut, PurchaseOrder
import reports.models as reports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import DecimalField
from decimal import Decimal
from django.utils.dateparse import parse_date
from users.utils import get_current_business
from expenses.models import Expense
from parties.models import Party
from sales.models import Invoice
from purchase.models import Purchase
from datetime import datetime, timedelta
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    business = get_current_business(request.user)  # If you use business context
    # Fetch sales-related transactions
    sales_data = list(Invoice.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('invoice_no'),
        type=Value('Invoice', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))
    
    sales_data += list(Quotation.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('quotation_no'),
        type=Value('Quotation', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    sales_data += list(SalesReturn.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('salesreturn_no'),
        type=Value('SalesReturn', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    sales_data += list(PaymentIn.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('payment_in_number'),
        type=Value('PaymentIn', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        # payment_amount=F('amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    sales_data += list(DeliveryChallan.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('delivery_challan_no'),
        type=Value('DeliveryChallan', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    sales_data += list(CreditNote.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('credit_note_no'),
        type=Value('CreditNote', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    sales_data += list(Proforma.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('proforma_no'),
        type=Value('Proforma', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))
    
    # Fetch purchase-related transactions
    purchase_data = list(Purchase.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('purchase_no'),
        type=Value('Purchase', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))  # No annotation needed

    purchase_data += list(PurchaseReturn.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('purchasereturn_no'),
        type=Value('PurchaseReturn', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    
    purchase_data += list(DebitNote.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('debitnote_no'),
        type=Value('DebitNote', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    
    purchase_data += list(PaymentOut.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('payment_out_number'),
        type=Value('PaymentOut', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        # payment_amount=F('amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    purchase_data += list(PurchaseOrder.objects.filter(business=business).annotate(
        tid=F('id'),
        transaction_no=F('purchase_order_no'),
        type=Value('PurchaseOrder', output_field=CharField()),
        party_name=F('party__party_name'),  # Correctly fetching related party name
        amount=F('total_amount')  # Correctly fetching related party name
    ).values('tid','date', 'transaction_no', 'type', 'party_name','amount'))

    
    for data in purchase_data:
        data['date'] = data.pop('date', None)

    # Merge and sort by date (newest first)
    transactions = sorted(sales_data +  purchase_data  , key=lambda x: x['date']or "", reverse=True)

    return JsonResponse({'transactions': transactions}, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_profit(request):
    business = get_current_business(request.user)  # If you use business context

    # Get start and end dates from query parameters (if provided)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)

    # 1. Sales (+)
    invoice_qs = Invoice.objects.filter(business=business)
    if start_date:
        invoice_qs = invoice_qs.filter(date__gte=start_date)
    if end_date:
        invoice_qs = invoice_qs.filter(date__lte=end_date)
    total_sales = invoice_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal(0)

    # 2. Credit Notes (-)
    credit_qs = CreditNote.objects.filter(business=business)
    if start_date:
        credit_qs = credit_qs.filter(date__gte=start_date)
    if end_date:
        credit_qs = credit_qs.filter(date__lte=end_date)
    total_credit_notes = credit_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal(0)

    # 3. Purchases (+)
    purchase_qs = Purchase.objects.filter(business=business)
    if start_date:
        purchase_qs = purchase_qs.filter(date__gte=start_date)
    if end_date:
        purchase_qs = purchase_qs.filter(date__lte=end_date)
    total_purchases = purchase_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal(0)

    # 4. Debit Notes (-)
    debit_qs = DebitNote.objects.filter(business=business)
    if start_date:
        debit_qs = debit_qs.filter(date__gte=start_date)
    if end_date:
        debit_qs = debit_qs.filter(date__lte=end_date)
    total_debit_notes = debit_qs.aggregate(total=Sum('total_amount'))['total'] or Decimal(0)

    # 5. Gross Profit
    cogs = total_purchases - total_debit_notes
    gross_profit = total_sales - cogs

    return JsonResponse({
        'total_sales': round(total_sales, 2),
        'total_credit_notes': round(total_credit_notes, 2),
        'total_purchases': round(total_purchases, 2),
        'total_debit_notes': round(total_debit_notes, 2),
        'gross_profit': round(gross_profit, 2),
    }, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_counts(request):
    business = get_current_business(request.user)
    period = request.GET.get('period', 'yearly')  # default to yearly

    now = timezone.now()
    if period == 'monthly':
        start_date = now.replace(day=1)
    elif period == 'weekly':
        start_date = now - timedelta(days=now.weekday())  # Monday of this week
    else:  # yearly
        start_date = now.replace(month=1, day=1)

    # Filter by business and date
    sales = Invoice.objects.filter(business=business, date__gte=start_date).count()
    purchase = Purchase.objects.filter(business=business, date__gte=start_date).count()
    expenses = Expense.objects.filter(business=business, date__gte=start_date).count()
    parties = Party.objects.filter(business=business, created_at__gte=start_date).count()  # Assuming Party has created_at

    return JsonResponse({
        'sales': sales,
        'purchase': purchase,
        'expenses': expenses,
        'parties': parties,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_parties_combined(request):
    business = get_current_business(request.user)
    period = request.GET.get('period', 'yearly')
    now = timezone.now()

    if period == 'monthly':
        start_date = now.replace(day=1)
    elif period == 'weekly':
        start_date = now - timedelta(days=now.weekday())
    else:  # yearly
        start_date = now.replace(month=1, day=1)

    # Get all parties with their sales and purchase stats
    

    parties = (
        Party.objects.filter(business=business)
        .annotate(
            total_sales=Count('invoice', filter=Q(invoice__date__gte=start_date)),
            total_revenue=Sum('invoice__total_amount', filter=Q(invoice__date__gte=start_date)),
            total_purchases=Count('purchase', filter=Q(purchase__date__gte=start_date)),
            total_purchase_amount=Sum('purchase__total_amount', filter=Q(purchase__date__gte=start_date)),
        )
        .order_by('-total_revenue')[:5]
    )

    data = []
    for party in parties:
        data.append({
            'id': party.id,
            'name': party.party_name,
            'total_sales': party.total_sales or 0,
            'total_revenue': float(party.total_revenue or 0),
            'total_purchases': party.total_purchases or 0,
            'total_purchase_amount': float(party.total_purchase_amount or 0),
        })

    return JsonResponse({'parties': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_total_profit(request):
    business = get_current_business(request.user)

    # Optional date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
    if end_date:
        end_date = parse_date(end_date)

    # Revenue from Invoices
    invoices = Invoice.objects.filter(business=business)
    if start_date:
        invoices = invoices.filter(date__gte=start_date)
    if end_date:
        invoices = invoices.filter(date__lte=end_date)
    total_revenue = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Purchase Costs
    purchases = Purchase.objects.filter(business=business)
    if start_date:
        purchases = purchases.filter(date__gte=start_date)
    if end_date:
        purchases = purchases.filter(date__lte=end_date)
    total_purchases = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Expenses
    expenses = Expense.objects.filter(business=business)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    total_expenses = expenses.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Total Profit = Revenue - Purchases - Expenses
    total_profit = total_revenue - total_purchases - total_expenses

    return JsonResponse({
        'total_revenue': round(total_revenue, 2),
        'total_purchases': round(total_purchases, 2),
        'total_expenses': round(total_expenses, 2),
        'total_profit': round(total_profit, 2),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_total_revenue(request):
    business = get_current_business(request.user)
    period = request.GET.get('period', 'yearly')
    now = timezone.now()

    # 📅 Determine period start
    if period == 'monthly':
        start_date = now.replace(day=1)
    elif period == 'weekly':
        start_date = now - timedelta(days=now.weekday())  # Monday
    else:  # yearly or default
        start_date = now.replace(month=1, day=1)

    # 🔢 Total revenue from all parties (via invoices)
    total_revenue = (
        Party.objects.filter(business=business)
        .aggregate(
            total=Sum('invoice__total_amount', filter=Q(invoice__date__gte=start_date))
        )['total'] or 0
    )

    return JsonResponse({
        'period': period,
        'start_date': start_date.date(),
        'total_revenue': round(float(total_revenue), 2),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_revenue_data(request):
    business = get_current_business(request.user)
    
    # Get date range from query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse({'error': 'start_date and end_date are required'}, status=400)
    
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    
    # Get all invoices within date range
    invoices = Invoice.objects.filter(
        business=business,
        date__range=[start_date, end_date]
    )
    
    # Get all credit notes within date range
    credit_notes = CreditNote.objects.filter(
        business=business,
        date__range=[start_date, end_date]
    )
    
    # Calculate total revenue
    total_invoice_amount = invoices.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    total_credit_note_amount = credit_notes.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # Net revenue = Total invoices - Total credit notes
    net_revenue = total_invoice_amount - total_credit_note_amount
    
    # Get daily revenue data for the chart
    daily_revenue = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # Get revenue for current day
        day_invoices = invoices.filter(date=current_date)
        day_credit_notes = credit_notes.filter(date=current_date)
        
        day_invoice_amount = day_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        day_credit_note_amount = day_credit_notes.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        daily_revenue.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'amount': float(day_invoice_amount - day_credit_note_amount)
        })
        
        current_date = next_date
    
    return JsonResponse({
        'total_revenue': float(net_revenue),
        'daily_revenue': daily_revenue
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profit_data(request):
    business = get_current_business(request.user)
    
    # Get date range from query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date or not end_date:
        return JsonResponse({'error': 'start_date and end_date are required'}, status=400)
    
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    
    # Get all invoices and purchases within date range
    invoices = Invoice.objects.filter(
        business=business,
        date__range=[start_date, end_date]
    )
    
    purchases = Purchase.objects.filter(
        business=business,
        date__range=[start_date, end_date]
    )
    
    credit_notes = CreditNote.objects.filter(
        business=business,
        date__range=[start_date, end_date]
    )
    
    debit_notes = DebitNote.objects.filter(
        business=business,
        date__range=[start_date, end_date]
    )
    
    # Calculate totals
    total_sales = invoices.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    total_purchases = purchases.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    total_credit_notes = credit_notes.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    total_debit_notes = debit_notes.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # Calculate net profit
    net_sales = total_sales - total_credit_notes
    net_purchases = total_purchases - total_debit_notes
    gross_profit = net_sales - net_purchases
    
    # Get daily profit data for the chart
    daily_profit = []
    current_date = start_date
    
    while current_date <= end_date:
        next_date = current_date + timedelta(days=1)
        
        # Get data for current day
        day_invoices = invoices.filter(date=current_date)
        day_purchases = purchases.filter(date=current_date)
        day_credit_notes = credit_notes.filter(date=current_date)
        day_debit_notes = debit_notes.filter(date=current_date)
        
        # Calculate day's totals
        day_sales = day_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        day_purchases = day_purchases.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        day_credit_notes = day_credit_notes.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        day_debit_notes = day_debit_notes.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Calculate day's profit
        day_net_sales = day_sales - day_credit_notes
        day_net_purchases = day_purchases - day_debit_notes
        day_profit = day_net_sales - day_net_purchases
        
        daily_profit.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'amount': float(day_profit)
        })
        
        current_date = next_date
    
    return JsonResponse({
        'total_profit': float(gross_profit),
        'daily_profit': daily_profit
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_yearly_earnings(request):
    business = get_current_business(request.user)
    year = request.GET.get('year', str(datetime.now().year))
    
    try:
        year = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid year format'}, status=400)
    
    # Initialize monthly data array
    monthly_data = []
    
    for month in range(1, 13):
        # Calculate start and end dates for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Get invoices for the month
        month_invoices = Invoice.objects.filter(
            business=business,
            date__range=[start_date, end_date]
        )
        
        # Get credit notes for the month
        month_credit_notes = CreditNote.objects.filter(
            business=business,
            date__range=[start_date, end_date]
        )
        
        # Get purchases for the month
        month_purchases = Purchase.objects.filter(
            business=business,
            date__range=[start_date, end_date]
        )
        
        # Get debit notes for the month
        month_debit_notes = DebitNote.objects.filter(
            business=business,
            date__range=[start_date, end_date]
        )
        
        # Calculate totals for the month
        total_sales = month_invoices.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_credit_notes = month_credit_notes.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_purchases = month_purchases.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        total_debit_notes = month_debit_notes.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
        
        # Calculate net earnings for the month
        net_sales = total_sales - total_credit_notes
        net_purchases = total_purchases - total_debit_notes
        monthly_earnings = net_sales - net_purchases
        
        monthly_data.append({
            'month': month,
            'earnings': float(monthly_earnings),
            'sales': float(net_sales),
            'purchases': float(net_purchases)
        })
    
    # Calculate yearly totals
    yearly_totals = {
        'total_earnings': sum(item['earnings'] for item in monthly_data),
        'total_sales': sum(item['sales'] for item in monthly_data),
        'total_purchases': sum(item['purchases'] for item in monthly_data)
    }
    
    return JsonResponse({
        'year': year,
        'monthly_data': monthly_data,
        'yearly_totals': yearly_totals
    })
