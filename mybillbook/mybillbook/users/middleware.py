from django.utils import timezone
from django.http import JsonResponse
from .models import Subscription, TrialSubscription
import json

class SubscriptionCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip subscription check for these paths
        excluded_paths = [
            '/users/login/',
            '/users/register/',
            '/users/plans/',
            '/users/subscribe/',
            '/users/create-trial/',
            '/users/check-subscription/',
        ]

        if request.path in excluded_paths or not request.user.is_authenticated:
            return self.get_response(request)

        # Check if user has an active subscription or trial
        has_active_subscription = False
        subscription_message = None

        if hasattr(request.user, 'business'):
            business = request.user.business
            
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

            if not subscription and not trial:
                has_active_subscription = False
                subscription_message = 'No active subscription found. Please subscribe to continue.'
            else:
                has_active_subscription = True

        if not has_active_subscription:
            return JsonResponse({
                'error': 'subscription_required',
                'message': subscription_message
            }, status=403)

        return self.get_response(request) 