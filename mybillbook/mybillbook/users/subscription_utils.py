from django.utils import timezone
from datetime import timedelta
from .models import Subscription, TrialSubscription, Business, User, Role
from django.db import transaction
from django.core.exceptions import ValidationError

def create_trial_subscription(business, user):
    """
    Create a trial subscription for a new business and its owner
    """
    with transaction.atomic():
        # Check if business already has a trial
        if TrialSubscription.objects.filter(business=business).exists():
            raise ValidationError("Business already has a trial subscription")

        # Create trial subscription
        trial = TrialSubscription.objects.create(
            business=business,
            end_date=timezone.now() + timedelta(days=14)
        )
        
        return trial

def validate_business_subscription(business):
    """
    Validate if a business has an active subscription or trial
    """
    # Check for active subscription
    subscription = Subscription.objects.filter(
        business=business,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()

    # Check for active trial
    trial = TrialSubscription.objects.filter(
        business=business,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()

    return bool(subscription or trial)

def validate_user_access(user, business):
    """
    Validate if a user has access to a business based on subscription status
    """
    # Check if user is owner
    is_owner = business.owner == user
    
    # Check if user is staff
    is_staff = Role.objects.filter(
        user=user,
        business=business,
        is_removed=False
    ).exists()

    if not (is_owner or is_staff):
        return False, "User is not associated with this business"

    # Check subscription status
    has_valid_subscription = validate_business_subscription(business)
    
    if not has_valid_subscription:
        if is_owner:
            return False, "Business subscription has expired. Please renew your subscription."
        else:
            return False, "Business subscription has expired. Please contact the business owner."

    return True, None

def check_trial_limits(business):
    """
    Check if trial usage is within limits
    Returns: (bool, str) - (is_within_limits, message)
    """
    trial = TrialSubscription.objects.filter(
        business=business,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()

    if not trial:
        return True, None  # Not in trial, so no limits apply

    # Example limits for trial
    staff_count = Role.objects.filter(business=business, is_removed=False).count()
    if staff_count > 3:  # Limit to 3 staff members in trial
        return False, "Trial plan limited to 3 staff members"

    return True, None

def handle_expired_subscription(business):
    """
    Handle expired subscription cases
    """
    # Deactivate expired subscriptions
    Subscription.objects.filter(
        business=business,
        is_active=True,
        end_date__lte=timezone.now()
    ).update(is_active=False)

    # Deactivate expired trials
    TrialSubscription.objects.filter(
        business=business,
        is_active=True,
        end_date__lte=timezone.now()
    ).update(is_active=False)

def validate_new_user_registration(mobile, email=None):
    """
    Validate if a new user registration is allowed
    """
    # Check if mobile already exists
    if User.objects.filter(mobile=mobile).exists():
        raise ValidationError("Mobile number already registered")

    # Check if email already exists (if provided)
    if email and User.objects.filter(email=email).exists():
        raise ValidationError("Email already registered")

    return True 