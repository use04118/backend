from rest_framework import serializers
from .models import User, Business, Role,SubscriptionPlan, Subscription,StaffInvite,AuditLog
from .utils import get_current_business
from reports.models import AuditTrail

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile', 'name', 'email', 'profile_picture']

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'id', 'name', 'phone', 'email',
            'business_address', 'street_address',
            'tcs','tds', 'gstin', 'business_type',
            'industry_type', 'registration_type',
            'pan_number', 'website', 'state', 'city', 'pincode','signature'
        ]

    def create(self, validated_data):
        user = self.context['request'].user

        # Remove owner if passed by mistake
        validated_data.pop('owner', None)

        # Create business with phone number from user
        business = Business.objects.create(
            owner=user,
            **validated_data
        )

        # Assign 'admin' role to the user for this business
        Role.objects.create(
            user=user,
            business=business,
            role_name='admin',
            permissions={"*": True}
        )

        return business

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class InviteStaffSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    name = serializers.CharField()
    role_name = serializers.ChoiceField(choices=Role.ROLE_CHOICES)
    business_id = serializers.IntegerField()

    def validate_mobile(self, mobile):
        request = self.context['request']
        business_id = self.initial_data.get("business_id")

        from users.models import Business, Role, StaffInvite

        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            raise serializers.ValidationError("Invalid business ID.")

        if Role.objects.filter(user__mobile=mobile, business=business).exists():
            raise serializers.ValidationError("This user is already part of the business.")

        if StaffInvite.objects.filter(mobile=mobile, business=business, status='accepted').exists():
            raise serializers.ValidationError("This user has already accepted an invite.")

        return mobile


class VerifyStaffOTPSerializer(serializers.Serializer):
    mobile = serializers.CharField()
    otp = serializers.CharField()

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'price', 'duration_days', 'features']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()

    class Meta:
        model = Subscription
        fields = ['plan', 'start_date', 'end_date', 'is_active']

import json
import logging
logger = logging.getLogger(__name__)

class AuditLogSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S')
    activity = serializers.CharField(source='action')
    user = serializers.SerializerMethodField()
    isEdited = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['timestamp', 'activity', 'details', 'amount', 'user', 'isEdited']

    def get_user(self, obj):
        request = self.context.get('request')
        if request and request.user == obj.user:
            return "YOU"
        
        if obj.user.name:
            display_name = obj.user.name
            # Get user's role in the business
            try:
                role = Role.objects.get(user=obj.user, business=obj.business, is_removed=False)
                if role.role_name == 'admin':
                    display_name += " (Admin)"
            except Role.DoesNotExist:
                pass
            return display_name
        return obj.user.mobile

    def get_isEdited(self, obj):
        action = obj.action.lower()
        return any(keyword in action for keyword in ['updated', 'edited', 'modified'])

    def get_details(self, obj):
        metadata = obj.metadata
        if not metadata:
            return ""
            
        # Handle different types of activities
        if 'invoice_number' in metadata:
            return f"Invoice #{metadata['invoice_number']}"
        elif 'purchase_number' in metadata:
            return f"Purchase #{metadata['purchase_number']}"
        elif 'quotation_number' in metadata:
            return f"Quotation #{metadata['quotation_number']}"
        elif 'name' in metadata and 'mobile' in metadata:
            return f"Staff: {metadata['name']} ({metadata['mobile']})"
        elif 'type' in metadata:
            return f"Login: {metadata['type']}"
        elif 'business_name' in metadata:
            return f"Business: {metadata['business_name']}"
        elif 'plan' in metadata:
            return f"Subscription: {metadata['plan']}"
        elif 'role_name' in metadata:
            return f"Role: {metadata['role_name']}"
        return metadata.get('details', '')

    def get_amount(self, obj):
        metadata = obj.metadata
        if not metadata:
            return None
            
        # Try to get amount from different possible fields
        amount = metadata.get('amount')
        if amount is not None:
            return amount
            
        # Try to get total_amount if amount is not present
        total_amount = metadata.get('total_amount')
        if total_amount is not None:
            return total_amount
            
        return None
