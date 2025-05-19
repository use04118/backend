from rest_framework import serializers, viewsets
from .models import Invoice, Quotation, SalesReturn, PaymentIn, CreditNote, DeliveryChallan, Proforma, InvoiceItem,QuotationItem,SalesReturnItem, DeliveryChallanItem, CreditNoteItem, ProformaItem,PaymentInInvoice
from inventory.models import Item, Service,GSTTaxRate # Your Item model,
from inventory.serializers import ItemSerializer
from rest_framework import serializers
from django.db import transaction
from .models import Invoice, InvoiceItem
from decimal import Decimal 
from django.db import transaction
from .models import Tcs, Tds
from users.utils import get_current_business
from cash_and_bank.models import BankAccount
from cash_and_bank.serializers import BankAccountSerializer
BANK_PAYMENT_METHODS = ["UPI", "Card", "Netbanking", "Bank Transfer", "Cheque"]

class TcsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tcs
        fields = ['id', 'rate', 'section', 'description', 'condition', 'business']
        read_only_fields = ['business']


class TdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tds
        fields = ['id', 'rate', 'section', 'description', 'business']
        read_only_fields = ['business']


class InvoiceItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.itemName', read_only=True)
    service_name = serializers.CharField(source='service.serviceName', read_only=True)
    available_stock = serializers.DecimalField(source='get_available_stock', read_only=True, max_digits=10, decimal_places=2)
    price_item = serializers.DecimalField(source='get_price_item', read_only=True, max_digits=10, decimal_places=2)
    amount = serializers.DecimalField(source='get_amount', read_only=True, max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    tax_rate_amount = serializers.DecimalField(source='get_tax_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cess_rate = serializers.DecimalField(source='gstTaxRate.cess_rate', read_only=True, max_digits=5, decimal_places=2)
    cess_rate_amount = serializers.DecimalField(source='get_cess_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cgst = serializers.DecimalField(source='get_cgst', read_only=True, max_digits=5, decimal_places=2)
    cgst_amount = serializers.DecimalField(source='get_cgst_amount', read_only=True, max_digits=10, decimal_places=2)
    igst = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    igst_amount = serializers.DecimalField(source='get_igst_amount', read_only=True, max_digits=10, decimal_places=2)
    sgst = serializers.DecimalField(source='get_sgst', read_only=True, max_digits=5, decimal_places=2)
    sgst_amount = serializers.DecimalField(source='get_sgst_amount', read_only=True, max_digits=10, decimal_places=2)
    hsnCode = serializers.CharField(source='item.hsnCode', read_only=True)
    sacCode = serializers.CharField(source='service.sacCode', read_only=True)
    salesPrice_with_tax = serializers.DecimalField(source='get_salesPrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_with_tax = serializers.DecimalField(source='get_purchasePrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPrice_without_tax = serializers.DecimalField(source='get_salesPrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_without_tax = serializers.DecimalField(source='get_purchasePrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPriceType = serializers.CharField(source='get_price_type', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'invoice', 'item', 'item_name', 'service', 'service_name', 
            'quantity', 'unit_price', 'amount', 'price_item', 'available_stock', 'gstTaxRate', 'discount',
            'tax_rate', 'tax_rate_amount', 'cess_rate', 'cess_rate_amount' , 'igst' , 'igst_amount' , 'cgst' , 'cgst_amount' , 'sgst', 'sgst_amount', 'hsnCode' , 'sacCode',
            'salesPrice_with_tax', 'purchasePrice_with_tax', 'salesPrice_without_tax', 'purchasePrice_without_tax', 'salesPriceType','type'
        ]
        extra_kwargs = {
            'invoice': {'required': False}  # 👈 This is the fix
        }

    def validate(self, data):
        """Ensure either item or service is provided, not both."""
        item = data.get('item')
        service = data.get('service')

        if not item and not service:
            raise serializers.ValidationError("Either 'item' or 'service' must be provided.")
        if item and service:
            raise serializers.ValidationError("You can only select either 'item' or 'service', not both.")
        if 'quantity' in data and data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")

        # Ensure stock availability for items
        if item:
            if item.closingStock < data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
        return data
    
    def create(self, validated_data):
        """Create InvoiceItem and deduct stock."""
        print("\n=== InvoiceItem Creation Debug ===")
        item = validated_data.get('item')
        print(f"Creating item: {item.itemName if item else 'Service'}")
        print(f"Quantity: {validated_data['quantity']}")
        if item:
            print(f"Initial stock: {item.closingStock}")
            print(f"Stock to deduct: {validated_data['quantity']}")
            print(f"Expected final stock: {item.closingStock - validated_data['quantity']}")

        invoice_item = InvoiceItem.objects.create(**validated_data)

        # ✅ Deduct stock if it's an item (not service)
        if item:
            item.closingStock -= validated_data['quantity']
            item.save()
            print(f"Final stock after deduction: {item.closingStock}")
            print("Stock deduction completed successfully")
        else:
            print("No stock deduction needed (service item)")

        return invoice_item
    
    def update(self, instance, validated_data):
        """Update InvoiceItem and reverse stock if needed."""
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        item = instance.item

        print(f"\n=== InvoiceItem Update Debug ===")
        print(f"Item: {item.itemName if item else 'Service'}")
        print(f"Old quantity: {old_quantity}")
        print(f"New quantity: {new_quantity}")
        print(f"Initial stock: {item.closingStock if item else 'N/A'}")

        # Handle stock adjustment
        if item:
            # Calculate the difference in quantity
            quantity_difference = new_quantity - old_quantity
            print(f"Quantity difference: {quantity_difference}")
            print(f"Current stock before adjustment: {item.closingStock}")
            
            # Only adjust stock if there's an actual change in quantity
            if quantity_difference != 0:
                if quantity_difference > 0:
                    # If increasing quantity, check if we have enough stock
                    if item.closingStock < quantity_difference:
                        raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
                    # Deduct the additional quantity
                    item.closingStock -= quantity_difference
                    print(f"Decreased stock by {quantity_difference}. New stock: {item.closingStock}")
                elif quantity_difference < 0:
                    # If decreasing quantity, add back the difference
                    item.closingStock += abs(quantity_difference)
                    print(f"Increased stock by {abs(quantity_difference)}. New stock: {item.closingStock}")
                
                item.save()
            else:
                print("No quantity change, skipping stock adjustment")

        # ✅ Update the InvoiceItem
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
        
    def delete(self, instance):
        """Reverse stock when item is deleted."""
        item = instance.item
        if item:
            item.closingStock += instance.quantity
            item.save()
        instance.delete()

class InvoiceSerializer(serializers.ModelSerializer):
    invoice_items = InvoiceItemSerializer(many=True, required=False)
    total_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    balance_amount = serializers.DecimalField(source='get_balance_amount', read_only=True, max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(source='get_taxable_amount', read_only=True, max_digits=10, decimal_places=2)
    tcs_on = serializers.ChoiceField(choices=Invoice.TCS_ON_CHOICES, required=False)
    tcs_amount = serializers.DecimalField(source='get_tcs_amount', read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)
    next_invoice_number = serializers.SerializerMethodField()
    bank_account = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Invoice
        fields = [
            'business', 'id', 'invoice_no', 'date', 'party', 'status',
            'payment_term', 'due_date', 'amount_received', 'is_fully_paid',
            'payment_method', 'discount', 'total_amount', 'balance_amount',
            'invoice_items', 'notes', 'signature', 'taxable_amount',
            'apply_tcs', 'tcs', 'tcs_on', 'tcs_amount', 'next_invoice_number',
            'bank_account'
        ]
        read_only_fields = [
            'business', 'total_amount', 'balance_amount',
            'taxable_amount', 'tcs_amount', 'next_invoice_number'
        ]

    def get_next_invoice_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return Invoice.get_next_invoice_number(business)
        return None

    def get_balance_amount(self, obj):
        # Ensure that both operands are of the same type (Decimal)
        total_amount = obj.get_total_amount()
        amount_received = Decimal(obj.amount_received)  # Convert amount_received to Decimal

        return total_amount - amount_received

    def validate(self, data):
        data = super().validate(data)
        
        # Validate bank account for non-cash payments
        payment_method = data.get('payment_method')
        if payment_method in BANK_PAYMENT_METHODS:
            bank_account = data.get('bank_account')
            if not bank_account:
                raise serializers.ValidationError({
                    "bank_account": "Bank account is required for non-cash payment methods"
                })
            
            # Verify bank account belongs to the business
            business = self.context['request'].user.current_business
            if bank_account.business != business:
                raise serializers.ValidationError({
                    "bank_account": "Invalid bank account"
                })
            
            # Verify it's a bank account (not cash)
            if bank_account.account_type != 'Bank':
                raise serializers.ValidationError({
                    "bank_account": "Selected account must be a bank account"
                })

        return data

    def create(self, validated_data):
        print("\n=== Invoice Creation Debug ===")
        invoice_items_data = validated_data.pop('invoice_items', [])
        print(f"Creating invoice with {len(invoice_items_data)} items")
            
        invoice = Invoice.objects.create(**validated_data)
        print(f"Created invoice: {invoice.invoice_no}")

        # ✅ Create each InvoiceItem using the serializer
        for idx, item_data in enumerate(invoice_items_data, 1):
            print(f"\nProcessing item {idx} of {len(invoice_items_data)}")
            
            # Convert model instances to primary keys
            if 'item' in item_data and hasattr(item_data['item'], 'id'):
                item_data['item'] = item_data['item'].id
            if 'service' in item_data and hasattr(item_data['service'], 'id'):
                item_data['service'] = item_data['service'].id
            if 'gstTaxRate' in item_data and hasattr(item_data['gstTaxRate'], 'id'):
                item_data['gstTaxRate'] = item_data['gstTaxRate'].id
            
            item_data['invoice'] = invoice.id  # Use invoice ID instead of instance
            print(f"Item data after conversion: {item_data}")
            
            try:
                # Use the serializer instead of direct model creation
                item_serializer = InvoiceItemSerializer(data=item_data)
                if item_serializer.is_valid():
                    item_serializer.save()
                    print(f"Successfully created item {idx}")
                else:
                    print(f"Validation errors for item {idx}: {item_serializer.errors}")
                    raise serializers.ValidationError(item_serializer.errors)
            except Exception as e:
                print(f"Error creating item {idx}: {str(e)}")
                raise

        # ✅ The save() method in Invoice will automatically update balance
        invoice.save()
        print("\nInvoice creation completed successfully")
        return invoice

    def update(self, instance, validated_data):
        """Update Invoice and its related InvoiceItems."""
        print("\n=== Invoice Update Debug ===")
        # Extract invoice_items from validated data
        invoice_items_data = validated_data.pop('invoice_items', [])
        
        # Calculate old total before any changes
        old_total = instance.get_total_amount()
        print(f"Old total before update: {old_total}")
        
        # Step 1: Update the main Invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Step 2: Handle InvoiceItem updates/deletions
        existing_items = instance.invoice_items.all()
        existing_item_map = {item.item.id if item.item else item.service.id: item for item in existing_items}
        
        # Convert all item references to IDs for comparison
        updated_item_ids = []
        for item_data in invoice_items_data:
            if 'item' in item_data:
                item = item_data['item']
                item_id = item.id if hasattr(item, 'id') else item
                updated_item_ids.append(item_id)
            elif 'service' in item_data:
                service = item_data['service']
                service_id = service.id if hasattr(service, 'id') else service
                updated_item_ids.append(service_id)
        
        print(f"\nExisting items: {list(existing_item_map.keys())}")
        print(f"Updated items: {updated_item_ids}")
        
        # Step 3: Delete removed items and update inventory
        for item_id in set(existing_item_map.keys()) - set(updated_item_ids):
            item_to_delete = existing_item_map[item_id]
            print(f"\nDeleting item ID: {item_id}")
            print(f"Item to delete: {item_to_delete.item.itemName if item_to_delete.item else item_to_delete.service.serviceName}")
            print(f"Current stock before deletion: {item_to_delete.item.closingStock if item_to_delete.item else 'N/A'}")
            # Delete the item using the serializer's delete method
            InvoiceItemSerializer().delete(item_to_delete)
            print(f"Stock after deletion: {item_to_delete.item.closingStock if item_to_delete.item else 'N/A'}")
        
        # Step 4: Update or Create new items
        for item_data in invoice_items_data:
            # Get the correct item ID regardless of whether it's a model instance or ID
            if 'item' in item_data:
                item = item_data['item']
                item_id = item.id if hasattr(item, 'id') else item
            else:
                service = item_data['service']
                item_id = service.id if hasattr(service, 'id') else service

            if item_id in existing_item_map:
                # Update existing item
                print(f"\nUpdating item ID: {item_id}")
                item_instance = existing_item_map[item_id]
                print(f"Item being updated: {item_instance.item.itemName if item_instance.item else item_instance.service.serviceName}")
                print(f"Current stock before update: {item_instance.item.closingStock if item_instance.item else 'N/A'}")
                
                # Handle stock adjustment
                if item_instance.item:
                    # Calculate the difference in quantity
                    quantity_difference = item_data['quantity'] - item_instance.quantity
                    print(f"Old quantity: {item_instance.quantity}")
                    print(f"New quantity: {item_data['quantity']}")
                    print(f"Quantity difference: {quantity_difference}")
                    
                    # Only adjust stock if there's an actual change in quantity
                    if quantity_difference != 0:
                        if quantity_difference > 0:
                            # If increasing quantity, check if we have enough stock
                            if item_instance.item.closingStock < quantity_difference:
                                raise serializers.ValidationError(f"Not enough stock for {item_instance.item.itemName}. Available: {item_instance.item.closingStock}")
                            # Deduct the additional quantity
                            item_instance.item.closingStock -= quantity_difference
                            print(f"Decreased stock by {quantity_difference}. New stock: {item_instance.item.closingStock}")
                        elif quantity_difference < 0:
                            # If decreasing quantity, add back the difference
                            item_instance.item.closingStock += abs(quantity_difference)
                            print(f"Increased stock by {abs(quantity_difference)}. New stock: {item_instance.item.closingStock}")
                        
                        item_instance.item.save()
                    else:
                        print("No quantity change, skipping stock adjustment")
                
                # Update the item
                for attr, value in item_data.items():
                    setattr(item_instance, attr, value)
                item_instance.save()
            else:
                # Create new item
                print(f"\nCreating new item")
                print(f"Item data: {item_data}")
                # Convert model instances to their primary keys
                if 'item' in item_data and hasattr(item_data['item'], 'id'):
                    item_data['item'] = item_data['item'].id
                if 'service' in item_data and hasattr(item_data['service'], 'id'):
                    item_data['service'] = item_data['service'].id
                if 'gstTaxRate' in item_data and hasattr(item_data['gstTaxRate'], 'id'):
                    item_data['gstTaxRate'] = item_data['gstTaxRate'].id
                
                item_data['invoice'] = instance.id
                serializer = InvoiceItemSerializer(data=item_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print(f"Validation errors: {serializer.errors}")
                    raise serializers.ValidationError(serializer.errors)
        
        # Step 5: Calculate new total after all changes
        new_total = instance.get_total_amount()
        print(f"\nNew total after update: {new_total}")
        
        # Step 6: Update party balance
        party = instance.party
        if party.balance_type == 'To Collect':
            # First reverse the old total
            party.closing_balance -= old_total
            # Then add the new total
            party.closing_balance += new_total
        elif party.balance_type == 'To Pay':
            # First reverse the old total
            party.closing_balance += old_total
            # Then subtract the new total
            party.closing_balance -= new_total
        
        party.save()
        print(f"Party balance after update: {party.closing_balance}")
        
        # Step 7: Save the invoice with updated totals
        instance.save()
        return instance


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class QuotationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.itemName', read_only=True)
    service_name = serializers.CharField(source='service.serviceName', read_only=True)
    available_stock = serializers.DecimalField(source='get_available_stock', read_only=True, max_digits=10, decimal_places=2)
    price_item = serializers.DecimalField(source='get_price_item', read_only=True, max_digits=10, decimal_places=2)
    amount = serializers.DecimalField(source='get_amount', read_only=True, max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    tax_rate_amount = serializers.DecimalField(source='get_tax_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cess_rate = serializers.DecimalField(source='gstTaxRate.cess_rate', read_only=True, max_digits=5, decimal_places=2)
    cess_rate_amount = serializers.DecimalField(source='get_cess_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cgst = serializers.DecimalField(source='get_cgst', read_only=True, max_digits=5, decimal_places=2)
    cgst_amount = serializers.DecimalField(source='get_cgst_amount', read_only=True, max_digits=10, decimal_places=2)
    igst = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    igst_amount = serializers.DecimalField(source='get_igst_amount', read_only=True, max_digits=10, decimal_places=2)
    sgst = serializers.DecimalField(source='get_sgst', read_only=True, max_digits=5, decimal_places=2)
    sgst_amount = serializers.DecimalField(source='get_sgst_amount', read_only=True, max_digits=10, decimal_places=2)
    hsnCode = serializers.CharField(source='item.hsnCode', read_only=True)
    sacCode = serializers.CharField(source='service.sacCode', read_only=True)
    salesPrice_with_tax = serializers.DecimalField(source='get_salesPrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_with_tax = serializers.DecimalField(source='get_purchasePrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPrice_without_tax = serializers.DecimalField(source='get_salesPrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_without_tax = serializers.DecimalField(source='get_purchasePrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPriceType = serializers.CharField(source='get_price_type', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)
    
    class Meta:
        model = QuotationItem
        fields = [
            'id', 'quotation', 'item', 'item_name', 'service', 'service_name', 
            'quantity', 'unit_price', 'amount', 'price_item', 'available_stock', 'gstTaxRate', 
            'tax_rate', 'tax_rate_amount', 'cess_rate', 'cess_rate_amount' , 'cgst' , 'cgst_amount' ,'igst' , 'igst_amount' ,'sgst', 'sgst_amount', 'hsnCode' , 'sacCode',
            'salesPrice_with_tax', 'purchasePrice_with_tax', 'salesPrice_without_tax', 'purchasePrice_without_tax', 'salesPriceType','type','discount'
        ]
        extra_kwargs = {
            'quotation': {'required': False}  # 👈 This is the fix
        }

    def validate(self, data):
        """Ensure either item or service is provided, not both."""
        item = data.get('item')
        service = data.get('service')

        if not item and not service:
            raise serializers.ValidationError("Either 'item' or 'service' must be provided.")
        if item and service:
            raise serializers.ValidationError("You can only select either 'item' or 'service', not both.")
        if 'quantity' in data and data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")

        # Ensure stock availability for items
        if item:
            if item.closingStock < data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
        return data
    

    def create(self, validated_data):
        """Create InvoiceItem and deduct stock."""
        item = validated_data.get('item')
        invoice_item = QuotationItem.objects.create(**validated_data)

        # ✅ Deduct stock if it's an item (not service)
        if item:
            item.closingStock -= validated_data['quantity']
            item.save()

        return invoice_item
    
    def update(self, instance, validated_data):
        """Update InvoiceItem and reverse stock if needed."""
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        item = instance.item

        # ✅ Reverse stock if item is being updated
        if item:
            item.closingStock += old_quantity  # Add back old stock
            item.save()

        # ✅ Deduct new stock if updated quantity is less
        if item and new_quantity > 0:
            if item.closingStock < new_quantity:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
            item.closingStock -= new_quantity
            item.save()

        # ✅ Update the InvoiceItem
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        print("""Reverse stock when item is deleted.""")
        item = instance.item
        if item:
            item.closingStock += instance.quantity
            item.save()
        instance.delete()

class QuotationSerializer(serializers.ModelSerializer):
    quotation_items = QuotationItemSerializer(many=True)
    total_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(source='get_taxable_amount', read_only=True, max_digits=10, decimal_places=2)
    balance_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)
    next_quotation_number = serializers.SerializerMethodField()

    class Meta:
        model = Quotation
        fields = fields = [
            'business','id', 'quotation_no', 'date', 'party', 'status', 
            'payment_term', 'due_date', 'discount', 'total_amount', 'balance_amount', 'quotation_items', 'notes' , 'signature' , 'taxable_amount','next_quotation_number'
        ]
        read_only_fields = ['business','next_quotation_number']

    
    def get_next_quotation_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return Quotation.get_next_quotation_number(business)
        return None

    def create(self, validated_data):
        print("create")
        invoice_items_data = validated_data.pop('quotation_items', [])   
        invoice = Quotation.objects.create(**validated_data)

        # ✅ Create each InvoiceItem without validation errors
        for item_data in invoice_items_data:
            item_data['quotation'] = invoice  # Inject invoice here after creation
            QuotationItem.objects.create(**item_data)

        # ✅ The save() method in Invoice will automatically update balance
        invoice.save()
        return invoice
 
    def update(self, instance, validated_data):
        print("Update")
        # Extract the invoice_items from validated data (if present)
        invoice_items_data = validated_data.pop('quotation_items', [])
       
        # Step 1: Update invoice fields (main Invoice object)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save the main Invoice model after updating its fields
        
        # Step 2: Handle InvoiceItem updates/deletions
        existing_items = instance.quotation_items.all()
        existing_item_ids = [item.id for item in existing_items]
        updated_item_ids = [item_data.get('id') for item_data in invoice_items_data if item_data.get('id')]

        # Step 3: Delete removed items
        for item_id in set(existing_item_ids) - set(updated_item_ids):
            item_to_delete = instance.quotation_items.get(id=item_id)
            QuotationItemSerializer().delete(item_to_delete)

        # Step 4: Update or Create new items
        for item_data in invoice_items_data:
            item_id = item_data.get('id')
            if item_id:
                # Update existing item
                item_instance = instance.quotation_items.get(id=item_id)
                if 'quantity' in item_data:
                    item_instance.quantity = item_data['quantity']

                QuotationItemSerializer().update(item_instance, item_data)
            else:
                # Create new item
                item_data['quotation'] = instance  # Associate the new InvoiceItem with the current Invoice
                QuotationItem.objects.create(**item_data)

        # Step 5: Automatically recalculate balance after saving changes
        instance.save()  # This ensures the updated Invoice object reflects the changes
        return instance
    
class QuotationViewSet(viewsets.ModelViewSet):
    queryset=Quotation.objects.all()
    serializer_class=QuotationSerializer


class SalesReturnItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.itemName', read_only=True)
    service_name = serializers.CharField(source='service.serviceName', read_only=True)
    available_stock = serializers.DecimalField(source='get_available_stock', read_only=True, max_digits=10, decimal_places=2)
    price_item = serializers.DecimalField(source='get_price_item', read_only=True, max_digits=10, decimal_places=2)
    amount = serializers.DecimalField(source='get_amount', read_only=True, max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    tax_rate_amount = serializers.DecimalField(source='get_tax_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cess_rate = serializers.DecimalField(source='gstTaxRate.cess_rate', read_only=True, max_digits=5, decimal_places=2)
    cess_rate_amount = serializers.DecimalField(source='get_cess_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cgst = serializers.DecimalField(source='get_cgst', read_only=True, max_digits=5, decimal_places=2)
    cgst_amount = serializers.DecimalField(source='get_cgst_amount', read_only=True, max_digits=10, decimal_places=2)
    igst = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    igst_amount = serializers.DecimalField(source='get_igst_amount', read_only=True, max_digits=10, decimal_places=2)
    sgst = serializers.DecimalField(source='get_sgst', read_only=True, max_digits=5, decimal_places=2)
    sgst_amount = serializers.DecimalField(source='get_sgst_amount', read_only=True, max_digits=10, decimal_places=2)
    hsnCode = serializers.CharField(source='item.hsnCode', read_only=True)
    sacCode = serializers.CharField(source='service.sacCode', read_only=True)
    salesPrice_with_tax = serializers.DecimalField(source='get_salesPrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_with_tax = serializers.DecimalField(source='get_purchasePrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPrice_without_tax = serializers.DecimalField(source='get_salesPrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_without_tax = serializers.DecimalField(source='get_purchasePrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPriceType = serializers.CharField(source='get_price_type', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)
    
    class Meta:
        model = SalesReturnItem
        fields = [
            'id', 'salesreturn', 'item', 'item_name', 'service', 'service_name', 
            'quantity', 'unit_price', 'amount', 'price_item', 'available_stock', 'gstTaxRate', 
            'tax_rate', 'tax_rate_amount', 'cess_rate', 'cess_rate_amount' , 'cgst' , 'cgst_amount' ,'igst' , 'igst_amount','sgst', 'sgst_amount', 'hsnCode' , 'sacCode',
        'salesPrice_with_tax', 'purchasePrice_with_tax', 'salesPrice_without_tax', 'purchasePrice_without_tax', 'salesPriceType','type','discount'
       ]
        extra_kwargs = {
            'salesreturn': {'required': False}  # 👈 This is the fix
        }

    def validate(self, data):
        """Ensure either item or service is provided, not both."""
        item = data.get('item')
        service = data.get('service')

        if not item and not service:
            raise serializers.ValidationError("Either 'item' or 'service' must be provided.")
        if item and service:
            raise serializers.ValidationError("You can only select either 'item' or 'service', not both.")
        if 'quantity' in data and data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")

        # Ensure stock availability for items
        if item:
            if item.closingStock < data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
        return data
    
    def create(self, validated_data):
        """Create InvoiceItem and deduct stock."""
        item = validated_data.get('item')
        invoice_item = SalesReturnItem.objects.create(**validated_data)

        # ✅ Deduct stock if it's an item (not service)
        if item:
            item.closingStock += validated_data['quantity']
            item.save()

        return invoice_item
    
    def update(self, instance, validated_data):
        """Update InvoiceItem and reverse stock if needed."""
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        item = instance.item

        # ✅ Reverse stock if item is being updated
        if item:
            item.closingStock += old_quantity  # Add back old stock
            item.save()

        # ✅ Deduct new stock if updated quantity is less
        if item and new_quantity > 0:
            if item.closingStock < new_quantity:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
            item.closingStock -= new_quantity
            item.save()

        # ✅ Update the InvoiceItem
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        """Reverse stock when item is deleted."""
        item = instance.item
        if item:
            item.closingStock += instance.quantity
            item.save()
        instance.delete()

class SalesReturnSerializer(serializers.ModelSerializer):
    salesreturn_items = SalesReturnItemSerializer(many=True, required=False)
    total_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(source='get_taxable_amount', read_only=True, max_digits=10, decimal_places=2)
    balance_amount = serializers.DecimalField(source='get_balance_amount', read_only=True, max_digits=10, decimal_places=2)
    tcs_on = serializers.ChoiceField(choices=Invoice.TCS_ON_CHOICES, required=False)
    tcs_amount = serializers.DecimalField(source='get_tcs_amount', read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)
    next_salesreturn_number = serializers.SerializerMethodField()
    bank_account = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.all(),
        required=False,
        allow_null=True
    )


    class Meta:
        model = SalesReturn
        fields = [
            'business','id', 'salesreturn_no', 'date', 'party', 'status', 
            'amount_received', 'is_fully_paid','invoice_no','invoice_id',
            'payment_method', 'discount', 'total_amount', 'balance_amount', 'salesreturn_items', 'notes' , 'signature' ,'taxable_amount',
            'apply_tcs', 'tcs', 'tcs_on', 'tcs_amount','next_salesreturn_number','bank_account'
        ]
        read_only_fields = ['business', 'total_amount', 'balance_amount',
            'taxable_amount', 'tcs_amount','next_salesreturn_number' ]
    
    def get_next_salesreturn_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return SalesReturn.get_next_salesreturn_number(business)
        return None
    
    
    def get_balance_amount(self, obj):
        # Ensure that both operands are of the same type (Decimal)
        total_amount = obj.get_total_amount()
        amount_received = Decimal(obj.amount_received)  # Convert amount_received to Decimal

        return total_amount - amount_received
    
    def validate(self, data):
        data = super().validate(data)
        # Validate bank account for non-cash payments
        payment_method = data.get('payment_method')
        if payment_method in BANK_PAYMENT_METHODS:
            bank_account = data.get('bank_account')
            if not bank_account:
                raise serializers.ValidationError({
                    "bank_account": "Bank account is required for non-cash payment methods"
                })
            
            # Verify bank account belongs to the business
            business = self.context['request'].user.current_business
            if bank_account.business != business:
                raise serializers.ValidationError({
                    "bank_account": "Invalid bank account"
                })
            
            # Verify it's a bank account (not cash)
            if bank_account.account_type != 'Bank':
                raise serializers.ValidationError({
                    "bank_account": "Selected account must be a bank account"
                })

        return data

    def create(self, validated_data):
        print("create")
        invoice_items_data = validated_data.pop('salesreturn_items', [])
            
        invoice = SalesReturn.objects.create(**validated_data)

        # ✅ Create each InvoiceItem without validation errors
        for item_data in invoice_items_data:
            item_data['salesreturn'] = invoice  # Inject invoice here after creation
            SalesReturnItem.objects.create(**item_data)


        # ✅ The save() method in Invoice will automatically update balance
        invoice.save()
        return invoice

    def update(self, instance, validated_data):
        invoice_items_data = validated_data.pop('salesreturn_items', [])

        # ✅ Step 1: Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ✅ Step 2: Handle InvoiceItem update/delete
        existing_items = instance.salesreturn_items.all()
        existing_item_ids = [item.id for item in existing_items]
        updated_item_ids = [item_data.get('id') for item_data in invoice_items_data if item_data.get('id')]

        # ✅ Step 3: Delete removed items
        for item_id in set(existing_item_ids) - set(updated_item_ids):
            item_to_delete = instance.salesreturn_items.get(id=item_id)
            SalesReturnItemSerializer().delete(item_to_delete)

        # ✅ Step 4: Update or Create new items
        for item_data in invoice_items_data:
            item_id = item_data.get('id')
            if item_id:
                # Update existing item
                item_instance = instance.salesreturn_items.get(id=item_id)
                SalesReturnItemSerializer().update(item_instance, item_data)
            else:
                # Create new item
                item_data['salesreturn'] = instance
                SalesReturnItem.objects.create(**item_data)

        # ✅ Step 5: Automatically recalculate balance after saving changes
        instance.save()
        return instance

class SalesReturnViewSet(viewsets.ModelViewSet):
    queryset=SalesReturn.objects.all()
    serializer_class=SalesReturnSerializer


class InvoiceSettlementSerializer(serializers.Serializer):
    invoice = serializers.PrimaryKeyRelatedField(queryset=Invoice.objects.all())
    settled_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    apply_tds = serializers.BooleanField(default=False)
    tds_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)

    def validate(self, data):
        if data['apply_tds'] and data.get('tds_rate') is None:
            raise serializers.ValidationError("TDS rate must be provided if apply_tds is True.")
        return data

class PaymentInSerializer(serializers.ModelSerializer):
    settled_invoices = InvoiceSettlementSerializer(many=True, write_only=True)
    settled_invoice_details = serializers.SerializerMethodField()
    next_payment_in_number = serializers.SerializerMethodField()
    bank_account = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = PaymentIn
        fields = [
            'id', 'business', 'party', 'date', 'payment_mode', 'payment_in_number',
            'amount', 'notes', 'settled_invoices', 'settled_invoice_details','next_payment_in_number',
            'bank_account'
        ]
        read_only_fields = ['business', 'settled_invoice_details','next_payment_in_number']


    def validate(self, data):
        data = super().validate(data)
        
        # Validate bank account for non-cash payments
        payment_method = data.get('payment_method')
        if payment_method in BANK_PAYMENT_METHODS:
            bank_account = data.get('bank_account')
            if not bank_account:
                raise serializers.ValidationError({
                    "bank_account": "Bank account is required for non-cash payment methods"
                })
            
            # Verify bank account belongs to the business
            business = self.context['request'].user.current_business
            if bank_account.business != business:
                raise serializers.ValidationError({
                    "bank_account": "Invalid bank account"
                })
            
            # Verify it's a bank account (not cash)
            if bank_account.account_type != 'Bank':
                raise serializers.ValidationError({
                    "bank_account": "Selected account must be a bank account"
                })

        return data
    def get_settled_invoice_details(self, obj):
        return [
            {
                "invoice_id": record.invoice.id,
                "invoice_number": record.invoice.invoice_no,
                "settled_amount": record.settled_amount,
                "tds_applied": record.apply_tds,
                "tds_rate": record.tds_rate,
                "tds_amount": record.tds_amount
            }
            for record in PaymentInInvoice.objects.filter(payment_in=obj).select_related("invoice")
        ]

    def create(self, validated_data):
        settled_invoices_data = validated_data.pop('settled_invoices', [])
        payment_in = PaymentIn.objects.create(**validated_data)

        from .utils import apply_payment_to_invoices
        apply_payment_to_invoices(payment_in, settled_invoices_data)

        return payment_in
    
    def get_next_payment_in_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return PaymentIn.get_next_payment_in_number(business)
        return None
    

class CreditNoteItemSerializer(serializers.ModelSerializer):
    # Assuming 'item' and 'service' are ForeignKeys to 'Item' and 'Service' models
    item_name = serializers.CharField(source='item.itemName', read_only=True)
    service_name = serializers.CharField(source='service.serviceName', read_only=True)
    available_stock = serializers.DecimalField(source='get_available_stock', read_only=True, max_digits=10, decimal_places=2)
    price_item = serializers.DecimalField(source='get_price_item', read_only=True, max_digits=10, decimal_places=2)
    amount = serializers.DecimalField(source='get_amount', read_only=True, max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    tax_rate_amount = serializers.DecimalField(source='get_tax_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cess_rate = serializers.DecimalField(source='gstTaxRate.cess_rate', read_only=True, max_digits=5, decimal_places=2)
    cess_rate_amount = serializers.DecimalField(source='get_cess_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cgst = serializers.DecimalField(source='get_cgst', read_only=True, max_digits=5, decimal_places=2)
    cgst_amount = serializers.DecimalField(source='get_cgst_amount', read_only=True, max_digits=10, decimal_places=2)
    igst = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    igst_amount = serializers.DecimalField(source='get_igst_amount', read_only=True, max_digits=10, decimal_places=2)
    sgst = serializers.DecimalField(source='get_sgst', read_only=True, max_digits=5, decimal_places=2)
    sgst_amount = serializers.DecimalField(source='get_sgst_amount', read_only=True, max_digits=10, decimal_places=2)
    hsnCode = serializers.CharField(source='item.hsnCode', read_only=True)
    sacCode = serializers.CharField(source='service.sacCode', read_only=True)
    salesPrice_with_tax = serializers.DecimalField(source='get_salesPrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_with_tax = serializers.DecimalField(source='get_purchasePrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPrice_without_tax = serializers.DecimalField(source='get_salesPrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_without_tax = serializers.DecimalField(source='get_purchasePrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPriceType = serializers.CharField(source='get_price_type', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)
    

    class Meta:
        model = CreditNoteItem
        fields = ['id','creditnote','item', 'item_name', 'quantity', 'unit_price', 'amount','price_item', 'available_stock', 'service', 'service_name','gstTaxRate', 'tax_rate', 'tax_rate_amount', 'cess_rate', 'cess_rate_amount' , 'cgst' , 'cgst_amount','igst' , 'igst_amount' , 'sgst', 'sgst_amount','hsnCode','sacCode','salesPrice_with_tax', 'purchasePrice_with_tax', 'salesPrice_without_tax', 'purchasePrice_without_tax', 'salesPriceType','type','discount'
       ]
        extra_kwargs = {
            'creditnote': {'required': False}  # 👈 This is the fix
        }

    def validate(self, data):
        """Ensure either item or service is provided, not both."""
        item = data.get('item')
        service = data.get('service')

        if not item and not service:
            raise serializers.ValidationError("Either 'item' or 'service' must be provided.")
        if item and service:
            raise serializers.ValidationError("You can only select either 'item' or 'service', not both.")
        if 'quantity' in data and data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")

        # Ensure stock availability for items
        if item:
            if item.closingStock < data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
        return data
     
    def create(self, validated_data):
        """Create InvoiceItem and deduct stock."""
        item = validated_data.get('item')
        invoice_item = CreditNoteItem.objects.create(**validated_data)

        # ✅ Deduct stock if it's an item (not service)
        if item:
            item.closingStock += validated_data['quantity']
            item.save()

        return invoice_item
    
    def update(self, instance, validated_data):
        """Update InvoiceItem and reverse stock if needed."""
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        item = instance.item

        # ✅ Reverse stock if item is being updated
        if item:
            item.closingStock += old_quantity  # Add back old stock
            item.save()

        # ✅ Deduct new stock if updated quantity is less
        if item and new_quantity > 0:
            if item.closingStock < new_quantity:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
            item.closingStock -= new_quantity
            item.save()

        # ✅ Update the InvoiceItem
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        """Reverse stock when item is deleted."""
        item = instance.item
        if item:
            item.closingStock += instance.quantity
            item.save()
        instance.delete()

class CreditNoteSerializer(serializers.ModelSerializer):
    creditnote_items = CreditNoteItemSerializer(many=True)
    total_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    balance_amount = serializers.DecimalField(source='get_balance_amount', read_only=True, max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(source='get_taxable_amount', read_only=True, max_digits=10, decimal_places=2)
    tcs_on = serializers.ChoiceField(choices=Invoice.TCS_ON_CHOICES, required=False)
    tcs_amount = serializers.DecimalField(source='get_tcs_amount', read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)
    next_creditnote_number = serializers.SerializerMethodField()
    bank_account = serializers.PrimaryKeyRelatedField(
        queryset=BankAccount.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = CreditNote
        fields = ['business','id','credit_note_no', 'date', 'party', 'status', 'amount_received',
                  'is_fully_paid','payment_method', 'total_amount', 'balance_amount','creditnote_items','discount', 
                  'notes' , 'signature' , 'taxable_amount',
            'apply_tcs', 'tcs', 'tcs_on', 'tcs_amount' ,'salesreturn_no' , 'salesreturn_id','next_creditnote_number','bank_account']
        
        read_only_fields = ['business', 'total_amount', 'balance_amount',
            'taxable_amount', 'tcs_amount' ,'next_creditnote_number']
        
    def get_next_creditnote_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return CreditNote.get_next_creditnote_number(business)
        return None


    def get_balance_amount(self, obj):
        # Ensure that both operands are of the same type (Decimal)
        total_amount = obj.get_total_amount()
        amount_received = Decimal(obj.amount_received)  # Convert amount_received to Decimal

        return total_amount - amount_received
    
    def validate(self, data):
        data = super().validate(data)
        # Validate bank account for non-cash payments
        payment_method = data.get('payment_method')
        if payment_method in BANK_PAYMENT_METHODS:
            bank_account = data.get('bank_account')
            if not bank_account:
                raise serializers.ValidationError({
                    "bank_account": "Bank account is required for non-cash payment methods"
                })
            
            # Verify bank account belongs to the business
            business = self.context['request'].user.current_business
            if bank_account.business != business:
                raise serializers.ValidationError({
                    "bank_account": "Invalid bank account"
                })
            
            # Verify it's a bank account (not cash)
            if bank_account.account_type != 'Bank':
                raise serializers.ValidationError({
                    "bank_account": "Selected account must be a bank account"
                })

        return data

        
    def create(self, validated_data):
        invoice_items_data = validated_data.pop('creditnote_items')
        invoice = CreditNote.objects.create(**validated_data)

        # Create invoice items and associate them with the invoice
        for item_data in invoice_items_data:
            item_data['creditnote'] = invoice  # Set the foreign key to the created invoice
            CreditNoteItem.objects.create(**item_data)

        invoice.save()
        return invoice

    def update(self, instance, validated_data):
        invoice_items_data = validated_data.pop('creditnote_items', [])


        # ✅ Step 1: Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ✅ Step 2: Handle InvoiceItem update/delete
        existing_items = instance.creditnote_items.all()
        existing_item_ids = [item.id for item in existing_items]
        updated_item_ids = [item_data.get('id') for item_data in invoice_items_data if item_data.get('id')]

        # ✅ Step 3: Delete removed items
        for item_id in set(existing_item_ids) - set(updated_item_ids):
            item_to_delete = instance.creditnote_items.get(id=item_id)
            CreditNoteItemSerializer().delete(item_to_delete)

        # ✅ Step 4: Update or Create new items
        for item_data in invoice_items_data:
            item_id = item_data.get('id')
            if item_id:
                # Update existing item
                item_instance = instance.creditnote_items.get(id=item_id)
                if 'quantity' in item_data:
                    item_instance.quantity = item_data['quantity']

                CreditNoteItemSerializer().update(item_instance, item_data)
            else:
                # Create new item
                item_data['creditnote'] = instance
                CreditNoteItem.objects.create(**item_data)

        # ✅ Step 5: Automatically recalculate balance
        instance.save()
        return instance

class CreditNoteViewSet(viewsets.ModelViewSet):
    queryset=CreditNote.objects.all()
    serializer_class=CreditNoteSerializer


class DeliveryChallanItemSerializer(serializers.ModelSerializer):
    # Assuming 'item' and 'service' are ForeignKeys to 'Item' and 'Service' models
    item_name = serializers.CharField(source='item.itemName', read_only=True)
    service_name = serializers.CharField(source='service.serviceName', read_only=True)
    available_stock = serializers.DecimalField(source='get_available_stock', read_only=True, max_digits=10, decimal_places=2)
    price_item = serializers.DecimalField(source='get_price_item', read_only=True, max_digits=10, decimal_places=2)
    amount = serializers.DecimalField(source='get_amount', read_only=True, max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    tax_rate_amount = serializers.DecimalField(source='get_tax_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cess_rate = serializers.DecimalField(source='gstTaxRate.cess_rate', read_only=True, max_digits=5, decimal_places=2)
    cess_rate_amount = serializers.DecimalField(source='get_cess_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cgst = serializers.DecimalField(source='get_cgst', read_only=True, max_digits=5, decimal_places=2)
    cgst_amount = serializers.DecimalField(source='get_cgst_amount', read_only=True, max_digits=10, decimal_places=2)
    igst = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    igst_amount = serializers.DecimalField(source='get_igst_amount', read_only=True, max_digits=10, decimal_places=2)
    sgst = serializers.DecimalField(source='get_sgst', read_only=True, max_digits=5, decimal_places=2)
    sgst_amount = serializers.DecimalField(source='get_sgst_amount', read_only=True, max_digits=10, decimal_places=2)
    hsnCode = serializers.CharField(source='item.hsnCode', read_only=True)
    sacCode = serializers.CharField(source='service.sacCode', read_only=True)
    salesPrice_with_tax = serializers.DecimalField(source='get_salesPrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_with_tax = serializers.DecimalField(source='get_purchasePrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPrice_without_tax = serializers.DecimalField(source='get_salesPrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_without_tax = serializers.DecimalField(source='get_purchasePrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPriceType = serializers.CharField(source='get_price_type', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)
    

    class Meta:
        model = DeliveryChallanItem
        fields = [ 'id','deliverychallan','item', 'item_name', 'unit_price', 'quantity', 'amount', 'price_item','available_stock','gstTaxRate' ,'service', 'service_name','tax_rate', 'tax_rate_amount', 'cess_rate', 'cess_rate_amount' , 'cgst' , 'cgst_amount' ,'igst' , 'igst_amount', 'sgst', 'sgst_amount','hsnCode','sacCode','salesPrice_with_tax', 'purchasePrice_with_tax', 'salesPrice_without_tax', 'purchasePrice_without_tax', 'salesPriceType','type','discount'
        ]
        
        extra_kwargs = {
            'deliverychallan': {'required': False}  # 👈 This is the fix
        }

    def validate(self, data):
        """Ensure either item or service is provided, not both."""
        item = data.get('item')
        service = data.get('service')

        if not item and not service:
            raise serializers.ValidationError("Either 'item' or 'service' must be provided.")
        if item and service:
            raise serializers.ValidationError("You can only select either 'item' or 'service', not both.")
        if 'quantity' in data and data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")

        # Ensure stock availability for items
        if item:
            if item.closingStock < data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
        return data
    

    def create(self, validated_data):
        """Create InvoiceItem and deduct stock."""
        item = validated_data.get('item')
        invoice_item = DeliveryChallanItem.objects.create(**validated_data)

        # ✅ Deduct stock if it's an item (not service)
        if item:
            item.closingStock -= validated_data['quantity']
            item.save()
        return invoice_item
    
    def update(self, instance, validated_data):
        """Update InvoiceItem and reverse stock if needed."""
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        item = instance.item

        # ✅ Reverse stock if item is being updated
        if item:
            item.closingStock += old_quantity  # Add back old stock
            item.save()

        # ✅ Deduct new stock if updated quantity is less
        if item and new_quantity > 0:
            if item.closingStock < new_quantity:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
            item.closingStock -= new_quantity
            item.save()

        # ✅ Update the InvoiceItem
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        print("""Reverse stock when item is deleted.""")
        item = instance.item
        if item:
            item.closingStock += instance.quantity
            item.save()
        instance.delete()
        
class DeliveryChallanSerializer(serializers.ModelSerializer):
    deliverychallan_items = DeliveryChallanItemSerializer(many=True)
    total_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(source='get_taxable_amount', read_only=True, max_digits=10, decimal_places=2)
    balance_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)
    next_deliverychallan_number = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryChallan
        fields = ['business','id','delivery_challan_no', 'date', 'party', 'status',  
                  'deliverychallan_items','discount', 'total_amount',
                  'balance_amount','notes' , 'signature' ,'taxable_amount','next_deliverychallan_number']
        read_only_fields = ['business','next_deliverychallan_number']

    def get_next_deliverychallan_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return DeliveryChallan.get_next_deliverychallan_number(business)
        return None


    # def get_balance_amount(self, obj):
    #     # Ensure obj is the model instance, not a dictionary
    #         total_amount = obj.get_total_amount()
    #         amount_received = Decimal(obj.amount_received) if obj.amount_received else Decimal(0)
    #         return total_amount - amount_received

    def create(self, validated_data):
        invoice_items_data = validated_data.pop('deliverychallan_items',[])
        invoice = DeliveryChallan.objects.create(**validated_data)

        for item_data in invoice_items_data:
            item_data['deliverychallan'] = invoice
            DeliveryChallanItem.objects.create(**item_data)
        
        invoice.save()
        return invoice
    
    def update(self, instance, validated_data):
        print("Update")
        # Extract the invoice_items from validated data (if present)
        invoice_items_data = validated_data.pop('deliverychallan_items', [])
       
        # Step 1: Update invoice fields (main Invoice object)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save the main Invoice model after updating its fields
        
        # Step 2: Handle InvoiceItem updates/deletions
        existing_items = instance.deliverychallan_items.all()
        existing_item_ids = [item.id for item in existing_items]
        updated_item_ids = [item_data.get('id') for item_data in invoice_items_data if item_data.get('id')]

        # Step 3: Delete removed items
        for item_id in set(existing_item_ids) - set(updated_item_ids):
            item_to_delete = instance.deliverychallan_items.get(id=item_id)
            DeliveryChallanItemSerializer().delete(item_to_delete)

        # Step 4: Update or Create new items
        for item_data in invoice_items_data:
            item_id = item_data.get('id')
            if item_id:
                # Update existing item
                item_instance = instance.deliverychallan_items.get(id=item_id)
                if 'quantity' in item_data:
                    item_instance.quantity = item_data['quantity']

                DeliveryChallanItemSerializer().update(item_instance, item_data)
            else:
                # Create new item
                item_data['deliverychallan'] = instance  # Associate the new InvoiceItem with the current Invoice
                DeliveryChallanItem.objects.create(**item_data)

        # Step 5: Automatically recalculate balance after saving changes
        instance.save()  # This ensures the updated Invoice object reflects the changes

        return instance  
  
class DeliveryChallanViewSet(viewsets.ModelViewSet):
    queryset=DeliveryChallan.objects.all()
    serializer_class=DeliveryChallanSerializer


class ProformaItemSerializer(serializers.ModelSerializer):
    # Assuming 'item' and 'service' are ForeignKeys to 'Item' and 'Service' models
    item_name = serializers.CharField(source='item.itemName', read_only=True)
    service_name = serializers.CharField(source='service.serviceName', read_only=True)
    available_stock = serializers.DecimalField(source='get_available_stock', read_only=True, max_digits=10, decimal_places=2)
    price_item = serializers.DecimalField(source='get_price_item', read_only=True, max_digits=10, decimal_places=2)
    amount = serializers.DecimalField(source='get_amount', read_only=True, max_digits=10, decimal_places=2)
    tax_rate = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    tax_rate_amount = serializers.DecimalField(source='get_tax_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cess_rate = serializers.DecimalField(source='gstTaxRate.cess_rate', read_only=True, max_digits=5, decimal_places=2)
    cess_rate_amount = serializers.DecimalField(source='get_cess_rate_amount', read_only=True, max_digits=10, decimal_places=2)
    cgst = serializers.DecimalField(source='get_cgst', read_only=True, max_digits=5, decimal_places=2)
    cgst_amount = serializers.DecimalField(source='get_cgst_amount', read_only=True, max_digits=10, decimal_places=2)
    igst = serializers.DecimalField(source='gstTaxRate.rate', read_only=True, max_digits=5, decimal_places=2)
    igst_amount = serializers.DecimalField(source='get_igst_amount', read_only=True, max_digits=10, decimal_places=2)
    sgst = serializers.DecimalField(source='get_sgst', read_only=True, max_digits=5, decimal_places=2)
    sgst_amount = serializers.DecimalField(source='get_sgst_amount', read_only=True, max_digits=10, decimal_places=2)
    hsnCode = serializers.CharField(source='item.hsnCode', read_only=True)
    sacCode = serializers.CharField(source='service.sacCode', read_only=True)
    salesPrice_with_tax = serializers.DecimalField(source='get_salesPrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_with_tax = serializers.DecimalField(source='get_purchasePrice_without_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPrice_without_tax = serializers.DecimalField(source='get_salesPrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    purchasePrice_without_tax = serializers.DecimalField(source='get_purchasePrice_with_tax', read_only=True, max_digits=5, decimal_places=2)
    salesPriceType = serializers.CharField(source='get_price_type', read_only=True)
    type = serializers.CharField(source='get_type', read_only=True)

    class Meta:
        model = ProformaItem
        fields = [ 'id','proforma','item', 'item_name', 'quantity', 'unit_price', 'amount', 'price_item','available_stock','gstTaxRate', 'service', 'service_name','tax_rate', 'tax_rate_amount', 'cess_rate', 'cess_rate_amount' , 'cgst' , 'cgst_amount' ,'igst' , 'igst_amount', 'sgst', 'sgst_amount','hsnCode','sacCode','salesPrice_with_tax', 'purchasePrice_with_tax', 'salesPrice_without_tax', 'purchasePrice_without_tax', 'salesPriceType','type','discount'
        ]
        
        extra_kwargs = {
            'proforma': {'required': False}  # 👈 This is the fix
        }

    def validate(self, data):
        """Ensure either item or service is provided, not both."""
        item = data.get('item')
        service = data.get('service')

        if not item and not service:
            raise serializers.ValidationError("Either 'item' or 'service' must be provided.")
        if item and service:
            raise serializers.ValidationError("You can only select either 'item' or 'service', not both.")
        if 'quantity' in data and data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")

        # Ensure stock availability for items
        if item:
            if item.closingStock < data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
        return data
    

    def create(self, validated_data):
        """Create InvoiceItem and deduct stock."""
        item = validated_data.get('item')
        invoice_item = DeliveryChallanItem.objects.create(**validated_data)

        # ✅ Deduct stock if it's an item (not service)
        if item:
            item.closingStock -= validated_data['quantity']
            item.save()

        return invoice_item
    
    def update(self, instance, validated_data):
        """Update InvoiceItem and reverse stock if needed."""
        old_quantity = instance.quantity
        new_quantity = validated_data.get('quantity', old_quantity)
        item = instance.item

        # ✅ Reverse stock if item is being updated
        if item:
            item.closingStock += old_quantity  # Add back old stock
            item.save()

        # ✅ Deduct new stock if updated quantity is less
        if item and new_quantity > 0:
            if item.closingStock < new_quantity:
                raise serializers.ValidationError(f"Not enough stock for {item.itemName}. Available: {item.closingStock}")
            item.closingStock -= new_quantity
            item.save()

        # ✅ Update the InvoiceItem
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        print("""Reverse stock when item is deleted.""")
        item = instance.item
        if item:
            item.closingStock += instance.quantity
            item.save()
        instance.delete()
    
class ProformaSerializer(serializers.ModelSerializer):
    proforma_items = ProformaItemSerializer(many=True)
    total_amount = serializers.DecimalField(source='get_total_amount',read_only=True, max_digits=10, decimal_places=2)
    taxable_amount = serializers.DecimalField(source='get_taxable_amount', read_only=True, max_digits=10, decimal_places=2)
    balance_amount = serializers.DecimalField(source='get_total_amount', read_only=True, max_digits=10, decimal_places=2)
    status = serializers.CharField(read_only=True)
    next_proforma_number = serializers.SerializerMethodField()

    class Meta:
        model = Proforma
        fields = ['business','id','proforma_no', 'date', 'party', 'status', 'payment_term', 
                  'due_date', 'proforma_items', 'discount', 'total_amount', 'balance_amount','notes' , 'signature' ,'taxable_amount','next_proforma_number']
        read_only_fields = ['business','next_proforma_number']

    def get_next_proforma_number(self, obj):
        request = self.context.get('request')
        if request and request.user:
            business = get_current_business(request.user)
            return Proforma.get_next_proforma_number(business)
        return None


    def create(self, validated_data):
        invoice_items_data = validated_data.pop('proforma_items',[])
        invoice = Proforma.objects.create(**validated_data)

        for item_data in invoice_items_data:
            item_data['proforma'] = invoice
            ProformaItem.objects.create(**item_data)
        
        invoice.save()
        return invoice
    
    def update(self, instance, validated_data):
        print("Update")
        # Extract the invoice_items from validated data (if present)
        invoice_items_data = validated_data.pop('proforma_items', [])
       
        # Step 1: Update invoice fields (main Invoice object)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()  # Save the main Invoice model after updating its fields
        
        # Step 2: Handle InvoiceItem updates/deletions
        existing_items = instance.proforma_items.all()
        existing_item_ids = [item.id for item in existing_items]
        updated_item_ids = [item_data.get('id') for item_data in invoice_items_data if item_data.get('id')]

        # Step 3: Delete removed items
        for item_id in set(existing_item_ids) - set(updated_item_ids):
            item_to_delete = instance.proforma_items.get(id=item_id)
            ProformaItemSerializer().delete(item_to_delete)

        # Step 4: Update or Create new items
        for item_data in invoice_items_data:
            item_id = item_data.get('id')
            if item_id:
                # Update existing item
                item_instance = instance.proforma_items.get(id=item_id)
                if 'quantity' in item_data:
                    item_instance.quantity = item_data['quantity']

                ProformaItemSerializer().update(item_instance, item_data)
            else:
                # Create new item
                item_data['proforma'] = instance  # Associate the new InvoiceItem with the current Invoice
                ProformaItem.objects.create(**item_data)

        # Step 5: Automatically recalculate balance after saving changes
        instance.save()  # This ensures the updated Invoice object reflects the changes

        return instance 
  
class ProformaViewSet(viewsets.ModelViewSet):
    queryset=Proforma.objects.all()
    serializer_class=ProformaSerializer
