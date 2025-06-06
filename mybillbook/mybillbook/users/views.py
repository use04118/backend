from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Business, Role,User,SubscriptionPlan,Subscription,StaffInvite,AuditLog,TrialSubscription
from rest_framework import status
import random
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from .serializers import UserProfileSerializer,InviteStaffSerializer, VerifyStaffOTPSerializer,SubscriptionPlanSerializer,BusinessSerializer,SubscriptionSerializer,AuditLogSerializer
from .permissions import IsBusinessAdmin,generate_permissions,activate_subscription,IsSuperAdmin
from .utils import get_current_business,has_subscription_feature,has_feature,has_permission,is_rate_limited,log_action
from .models import INDIAN_STATES , BUSINESS_TYPES, INDUSTRY_TYPES, REGISTRATION_TYPES
import logging
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from .subscription_utils import (
    create_trial_subscription,
    validate_business_subscription,
    validate_user_access,
    check_trial_limits,
    handle_expired_subscription,
    validate_new_user_registration
)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "mobile": request.user.mobile
        })

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class CreateBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BusinessSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    business = serializer.save(owner=request.user)
                    log_action(request.user, business, "business_created", {"name": business.name})
                    
                    # Create trial subscription for new business
                    trial = create_trial_subscription(business, request.user)
                    
                    # Set current business
                    request.user.current_business = business
                    request.user.save()
                
                return Response({
                    "message": "Business created with trial subscription",
                    "business": serializer.data,
                    "trial_end_date": trial.end_date
                }, status=201)
            except ValidationError as e:
                return Response({"error": str(e)}, status=400)
        return Response(serializer.errors, status=400)

class BusinessDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return (Business.objects.filter(owner=user) | Business.objects.filter(role__user=user)).distinct()

    def perform_destroy(self, instance):
        # Optional: Cascade delete related roles, invites, etc.
        instance.delete()

class DebugCacheView(APIView):
    def get(self, request):
        cache.set('test_key', 'hello', timeout=60)
        value = cache.get('test_key')
        return Response({"test_key": value})
    
class RequestOTPView(APIView):
    def post(self, request):
        mobile = request.data.get('mobile')
        if not mobile:
            return Response({"error": "Mobile number is required"}, status=400)

        # Rate limiting
        if is_rate_limited(mobile):
            return Response({"error": "Too many OTP requests. Try again later."}, status=429)

        # Generate and cache OTP
        otp = str(random.randint(100000, 999999))
        cache.set(f'otp_{mobile}', otp, timeout=300)  # 5 minutes
         # print(f"[Mocked OTP] OTP for {mobile}: {otp}",flush=True)
        logger = logging.getLogger(__name__)
        logger.info(f"[Mocked OTP] OTP for {mobile}: {otp}")

        # Initialize all flags
        user_exists = False
        owns_business = False
        is_staff = False
        invited_as_staff = False
        businesses = []

        # ✅ Check staff invite even if user doesn't exist
        invited_as_staff = StaffInvite.objects.filter(mobile=mobile, status='pending').exists()

        user = User.objects.filter(mobile=mobile).first()
        if user:
            user_exists = True
            owns_business = Business.objects.filter(owner=user).exists()
            is_staff = Role.objects.filter(user=user).exists()

            owned = Business.objects.filter(owner=user)
            member = Business.objects.filter(role__user=user)
            businesses = (owned | member).distinct().values("id", "name")

        return Response({
            "message": "OTP sent (mocked)",
            "user_exists": user_exists,
            "invited_as_staff": invited_as_staff,
            "owns_business": owns_business,
            "is_staff": is_staff,
            "businesses": list(businesses)
        })

class InviteStaffView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def post(self, request):
        serializer = InviteStaffSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            role_name = serializer.validated_data['role_name']
            name = serializer.validated_data['name']
            business_id = serializer.validated_data['business_id']

            try:
                business = Business.objects.get(id=business_id)
            except Business.DoesNotExist:
                return Response({"error": "Business not found"}, status=404)

            StaffInvite.objects.update_or_create(
                business=business,
                mobile=mobile,
                status='pending',
                defaults={
                    'name': name,
                    'role_name': role_name,
                    'invited_by': request.user,
                }
            )

            log_action(request.user, business, "staff_invited", {
                'name': name,
                "mobile": mobile,
                "role_name": role_name
            })

            login_url = "http://192.168.1.35:5173/auth/signin"
            print(
                f"[Invite Message] {mobile}: You've been invited to '{business.name}' as '{role_name}'. "
                f"Login at {login_url} using your number."
            )

            return Response({"message": "Staff invite message sent (mocked)"})
        return Response(serializer.errors, status=400)

class VerifyUnifiedOTPView(APIView):
    def post(self, request):
        mobile = request.data.get("mobile")
        otp = request.data.get("otp")
        if not mobile or not otp:
            return Response({"error": "Mobile and OTP required"}, status=400)

        # Validate OTP
        cached_otp = cache.get(f'otp_{mobile}')
        if otp != cached_otp:
            return Response({"error": "Invalid or expired OTP"}, status=400)

        # Get or create user
        user, created = User.objects.get_or_create(mobile=mobile)

        # Check staff invite
        invite = StaffInvite.objects.filter(mobile=mobile, status='pending').first()
        if invite:
            if not user.name:
                user.name = invite.name
            
            # Validate business subscription before adding staff
            if not validate_business_subscription(invite.business):
                return Response({
                    "error": "Business subscription has expired. Please contact the business owner."
                }, status=403)

            # Check trial limits
            is_within_limits, limit_message = check_trial_limits(invite.business)
            if not is_within_limits:
                return Response({"error": limit_message}, status=403)

            user.current_business = invite.business
            user.save(update_fields=["current_business", "name"])
            
            Role.objects.get_or_create(
                user=user,
                business=invite.business,
                role_name=invite.role_name,
                defaults={"permissions": generate_permissions(invite.role_name)}
            )
            
            invite.status = 'accepted'
            invite.save()

            log_action(
                user,
                invite.business,
                "staff_joined",
                {
                    "name": user.name,
                    "mobile": user.mobile,
                    "role_name": invite.role_name,
                    "business_name": invite.business.name
                }
            )

        # Delete OTP from cache
        cache.delete(f'otp_{mobile}')

        # Generate token
        refresh = RefreshToken.for_user(user)

        # Get businesses and roles
        owned = Business.objects.filter(owner=user)
        member = Business.objects.filter(role__user=user)
        all_businesses = (owned | member).distinct()
        biz_serializer = BusinessSerializer(all_businesses, many=True)

        role_data = [
            {
                "business_id": role.business.id,
                "business_name": role.business.name,
                "role": role.role_name
            }
            for role in Role.objects.filter(user=user)
        ]

        # Log the login
        current_business = invite.business if invite else user.current_business
        if current_business:
            log_action(
                user,
                current_business,
                "login",
                {
                    "type": "staff" if invite or Role.objects.filter(user=user, business=current_business).exists() else "admin",
                    "business_name": current_business.name
                }
            )

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user_id": user.id,
            "mobile": user.mobile,
            "businesses": biz_serializer.data,
            "roles": role_data
        })

class ListPendingInvitesView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def get(self, request):
        business = get_current_business(request.user)
        invites = StaffInvite.objects.filter(business=business, status='pending').order_by('-created_at')
        data = [
            {
                "mobile": invite.mobile,
                "role_name": invite.role_name,
                "invited_by": invite.invited_by.mobile if invite.invited_by else None,
                "created_at": invite.created_at
            }
            for invite in invites
        ]
        return Response({"pending_invites": data})
    
class ListStaffView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def get(self, request):
        business = get_current_business(request.user)

        staff = []

        # ✅ Accepted or removed users from Role
        roles = Role.objects.filter(business=business).select_related("user")
        joined_user_mobiles = []

        for role in roles:
            user = role.user
            joined_user_mobiles.append(user.mobile)

            status = "removed" if role.is_removed else "accepted"

            staff.append({
                "user_id": user.id,
                "name": user.name,
                "mobile": user.mobile,
                "role": role.role_name,
                "status": status,
                "permissions": role.permissions
            })

        # 🕒 Pending Invites (who haven't joined yet)
        pending_invites = StaffInvite.objects.filter(business=business, status='pending').exclude(mobile__in=joined_user_mobiles)

        for invite in pending_invites:
            staff.append({
                "user_id": None,
                "name": invite.name,
                "mobile": invite.mobile,
                "role": invite.role_name,
                "status": "pending",
                "permissions": generate_permissions(invite.role_name)
            })

        return Response({"staff": staff})

class ManagePendingInviteView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]
    
    def get(self, request):
        mobile = request.query_params.get("mobile")
        if not mobile:
            return Response({"error": "Mobile is required"}, status=400)

        business = get_current_business(request.user)

        try:
            invite = StaffInvite.objects.get(mobile=mobile, business=business, status='pending')
            return Response({
                "name": invite.name,
                "mobile": invite.mobile,
                "role_name": invite.role_name,
                "business_id": invite.business_id,
                "status": invite.status,
            })
        except StaffInvite.DoesNotExist:
            return Response({"error": "Pending invite not found"}, status=404)

    def patch(self, request):
        mobile = request.data.get("mobile")
        if not mobile:
            return Response({"error": "Mobile is required"}, status=400)

        business = get_current_business(request.user)

        try:
            invite = StaffInvite.objects.get(mobile=mobile, business=business, status='pending')
        except StaffInvite.DoesNotExist:
            return Response({"error": "Pending invite not found"}, status=404)

        # Update fields if they are provided
        updated_fields = []
        if "name" in request.data:
            invite.name = request.data["name"]
            updated_fields.append("name")
        if "role_name" in request.data:
            new_role = request.data["role_name"]
            if new_role not in dict(Role.ROLE_CHOICES):
                return Response({"error": "Invalid role"}, status=400)
            invite.role_name = new_role
            updated_fields.append("role_name")

        if updated_fields:
            invite.save(update_fields=updated_fields)
            return Response({"message": "Pending invite updated", "updated_fields": updated_fields})
        else:
            return Response({"message": "No fields to update"})


    def delete(self, request):
        mobile = request.data.get("mobile")
        if not mobile:
            return Response({"error": "Mobile is required"}, status=400)

        business = get_current_business(request.user)
        deleted, _ = StaffInvite.objects.filter(mobile=mobile, business=business, status='pending').delete()

        if deleted:
            return Response({"message": "Pending invite deleted"})
        return Response({"error": "No matching pending invite found"}, status=404)

class ResendStaffInviteView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def post(self, request):
        mobile = request.data.get("mobile")
        if not mobile:
            return Response({"error": "Mobile is required"}, status=400)

        business = get_current_business(request.user)

        try:
            invite = StaffInvite.objects.get(mobile=mobile, business=business, status='pending')
        except StaffInvite.DoesNotExist:
            return Response({"error": "No pending invite found"}, status=404)

        # Generate new OTP
        new_otp = str(random.randint(100000, 999999))
        invite.otp = new_otp
        invite.save()

        # Update ResendStaffInviteView response
        print(
            f"[Resent Invite] {invite.mobile}: Reminder - You've been invited to '{business.name}' as '{invite.role_name}'. "
            f"Login at http://192.168.1.35:5173/auth/signin using your number."
        )
        return Response({"message": "OTP resent to staff (mocked)"})

class UpdateStaffView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def get(self, request, user_id):
        business = get_current_business(request.user)
        try:
            role = Role.objects.select_related("user", "business").get(user__id=user_id, business=business)
        except Role.DoesNotExist:
            return Response({"error": "Staff not found in your business"}, status=404)

        data = {
            "user_id": role.user.id,
            "name": role.user.name,
            "mobile": role.user.mobile,
            "role": role.role_name,
            "permissions": role.permissions,
            "is_removed": getattr(role, "is_removed", False),
            "is_permanently_removed": getattr(role, "is_permanently_removed", False),
            "business_id": role.business.id
        }
        return Response(data)

    def patch(self, request, user_id):
        business = get_current_business(request.user)

        try:
            role = Role.objects.select_related("user").get(user__id=user_id, business=business)
        except Role.DoesNotExist:
            return Response({"error": "Staff not found in your business"}, status=404)

        user = role.user

        # Update name
        name = request.data.get("name")
        if name:
            user.name = name

        # Update mobile
        mobile = request.data.get("mobile")
        if mobile:
            user.mobile = mobile

        # Update role and permissions
        new_role_name = request.data.get("role_name")
        if new_role_name:
            if new_role_name not in dict(Role.ROLE_CHOICES):
                return Response({"error": "Invalid role"}, status=400)
            role.role_name = new_role_name
            role.permissions = generate_permissions(new_role_name)

        # Save changes
        user.save(update_fields=["name", "mobile"])
        role.save()

        return Response({"message": "Staff details updated"})

    def delete(self, request, user_id):
        business = get_current_business(request.user)
        try:
            role = Role.objects.select_related('user').get(user__id=user_id, business=business)
        except Role.DoesNotExist:
            return Response({"error": "Staff not found in your business"}, status=404)

        # Check if permanent removal is requested
        permanent = request.query_params.get('permanent', 'false').lower() == 'true'
        
        if permanent:
            # Get the user before deleting the role
            user = role.user
            
            # If this was their current business, clear it
            if user.current_business == business:
                user.current_business = None
                user.save(update_fields=['current_business'])
            
            # Delete any pending invites for this user and business
            StaffInvite.objects.filter(
                mobile=user.mobile,
                business=business,
                status='pending'
            ).delete()
            
            # Actually delete the role from database
            role.delete()
            
            log_action(
                request.user,
                business,
                "staff_permanently_removed",
                {
                    "name": user.name,
                    "mobile": user.mobile,
                    "role_name": role.role_name
                }
            )
            
            return Response({"message": "Staff permanently removed"})
        else:
            # Soft delete
            role.is_removed = True
            role.save(update_fields=["is_removed"])
            return Response({"message": "Staff removed (soft deleted)"})

class ReinviteStaffView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def post(self, request, user_id):
        business = get_current_business(request.user)
        try:
            role = Role.objects.select_related("user").get(
                user__id=user_id, 
                business=business,
                is_removed=True,
                is_permanently_removed=False
            )
        except Role.DoesNotExist:
            return Response({"error": "Staff not found or cannot be reinvited"}, status=404)

        # Create new staff invite
        StaffInvite.objects.create(
            business=business,
            mobile=role.user.mobile,
            name=role.user.name,
            role_name=role.role_name,
            invited_by=request.user,
            status='pending'
        )

        # Delete the old role
        role.delete()

        log_action(
            request.user,
            business,
            "staff_reinvited",
            {
                "name": role.user.name,
                "mobile": role.user.mobile,
                "role_name": role.role_name
            }
        )

        return Response({"message": "Staff reinvited successfully"})

class CurrentBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        business = user.current_business  # Direct from user object, no cache

        if not business:
            return Response({"error": "No active business selected"}, status=400)

        data = BusinessSerializer(business).data

        # Determine role
        if business.owner == user:
            data["role"] = "owner"
        else:
            role = Role.objects.filter(user=user, business=business).first()
            data["role"] = role.role_name if role else None

        return Response(data)

class MyBusinessesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        owned = Business.objects.filter(owner=user)
        member = Business.objects.filter(role__user=user)

        all_businesses = (owned | member).distinct()

        data = []
        for biz in all_businesses:
            biz_data = BusinessSerializer(biz).data
            if biz.owner == user:
                biz_data["role"] = "owner"
            else:
                role = Role.objects.filter(user=user, business=biz).first()
                biz_data["role"] = role.role_name if role else None

            data.append(biz_data)

        return Response({"businesses": data})

class SwitchBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        business_id = request.data.get("business_id")
        if not business_id:
            return Response({"error": "business_id is required"}, status=400)

        user = request.user
        try:
            business = Business.objects.get(id=business_id)

            # Ensure user belongs to this business
            is_owner = business.owner == user
            is_staff = Role.objects.filter(user=user, business=business).exists()
            if not (is_owner or is_staff):
                return Response({"error": "Not authorized for this business"}, status=403)

            user.current_business = business
            user.save(update_fields=['current_business'])
            log_action(user, business, "business_switched", {})

            role_name = "owner" if is_owner else Role.objects.get(user=user, business=business).role_name

            return Response({
                "message": "Business switched successfully",
                "business_id": business.id,
                "role": role_name
            })

        except Business.DoesNotExist:
            return Response({"error": "Business not found"}, status=404)

class ListPlansView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)

class SubscribeBusinessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            business = request.user.current_business

            if not business:
                return Response(
                    {'error': 'No active business selected'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check for existing active subscription
            existing_subscription = Subscription.objects.filter(
                business=business,
                is_active=True
            ).first()

            # Check for active trial
            trial_sub = TrialSubscription.objects.filter(
                business=business,
                is_active=True,
                end_date__gt=timezone.now()
            ).first()

            with transaction.atomic():
                # Deactivate trial if exists
                if trial_sub:
                    trial_sub.is_active = False
                    trial_sub.save()

                if existing_subscription:
                    # Update existing subscription
                    existing_subscription.plan = plan
                    existing_subscription.start_date = timezone.now()
                    existing_subscription.end_date = timezone.now() + timedelta(days=30)  # Assuming monthly subscription
                    existing_subscription.is_trial = plan.is_trial
                    existing_subscription.save()
                    subscription = existing_subscription
                else:
                    # Create new subscription if none exists
                    subscription = Subscription.objects.create(
                        business=business,
                        plan=plan,
                        start_date=timezone.now(),
                        end_date=timezone.now() + timedelta(days=30),  # Assuming monthly subscription
                        is_trial=plan.is_trial
                    )

            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Invalid plan'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CurrentSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        business = request.user.current_business
        
        if not business:
            return Response({
                'error': 'No active business selected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user access
        has_access, error_message = validate_user_access(request.user, business)
        if not has_access:
            return Response({'error': error_message}, status=status.HTTP_403_FORBIDDEN)

        # Handle expired subscriptions
        handle_expired_subscription(business)
        
        # Check for active subscription
        subscription = Subscription.objects.filter(
            business=business,
            is_active=True,
            end_date__gt=timezone.now()
        ).first()

        # If no active subscription, check for trial
        if not subscription:
            trial = TrialSubscription.objects.filter(
                business=business,
                is_active=True,
                end_date__gt=timezone.now()
            ).first()
            
            if trial:
                return Response({
                    'plan': 'Free Trial',
                    'start_date': trial.start_date,
                    'end_date': trial.end_date,
                    'is_active': True,
                    'is_trial': True
                })

        if subscription:
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)

class CheckSubscriptionStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        business = request.user.current_business
        
        if not business:
            return Response({
                'error': 'No active business selected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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

        if subscription or trial:
            return Response({'has_active_subscription': True})
        
        return Response({
            'has_active_subscription': False,
            'message': 'No active subscription found. Please subscribe to continue.'
        })

class CreateTrialSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        business = request.user.current_business
        
        if not business:
            return Response({
                'error': 'No active business selected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if business already has a trial
        existing_trial = TrialSubscription.objects.filter(business=business).exists()
        if existing_trial:
            return Response({
                'error': 'Trial subscription already used'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create trial subscription
        trial = TrialSubscription.objects.create(
            business=business,
            end_date=timezone.now() + timedelta(days=14)
        )

        return Response({
            'message': 'Trial subscription created successfully',
            'end_date': trial.end_date
        }, status=status.HTTP_201_CREATED)

class AuditLogListView(APIView):
    permission_classes = [IsAuthenticated, IsBusinessAdmin]

    def get(self, request):
        try:
            business = get_current_business(request.user)
            if not business:
                return Response({"error": "No active business found"}, status=400)

            logs = AuditLog.objects.filter(business=business).order_by('-created_at')[:100]
            serializer = AuditLogSerializer(logs, many=True, context={'request': request})
            
            return Response({
                "logs": serializer.data,
                "total": logs.count()
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class AllAuditLogsView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        logs = AuditLog.objects.all().order_by('-created_at')[:200]
        serializer = AuditLogSerializer(logs, many=True)
        return Response({"all_logs": serializer.data})

class IndianStatesView(APIView):
    permission_classes = [IsAuthenticated]  # Or use [IsAuthenticated] if needed

    def get(self, request):
        return Response([{'code': code, 'name': name} for code, name in INDIAN_STATES])
    
class IndustryTypeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([{'value': key, 'label': label} for key, label in INDUSTRY_TYPES])

class RegistrationTypeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([{'value': key, 'label': label} for key, label in REGISTRATION_TYPES])
    
class ValidateGSTDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, gstin):
        api_key = settings.GSTIN_API_KEY
        external_api_url = f"http://sheet.gstincheck.co.in/check/{api_key}/{gstin}"

        try:
            response = requests.get(external_api_url)

            # API call was successful
            if response.status_code == 200:
                data = response.json()

                # Check if the API has returned an error about token
                if "error" in data:
                    error_message = data.get("error", "").lower()
                    if "token" in error_message or "api key" in error_message:
                        return JsonResponse({"success": False, "error": "API key expired or token quota exceeded."}, status=401)

                # GSTIN valid case
                if data.get("flag"):  
                    return JsonResponse({"success": True, "data": data}, status=200)

                # GSTIN invalid case
                return JsonResponse({"success": False, "error": "Invalid GSTIN or data not found."}, status=400)

            # API key invalid or unauthorized
            elif response.status_code in [401, 403]:
                return JsonResponse({"success": False, "error": "Unauthorized or expired API key."}, status=401)

            # Other unexpected statuses
            else:
                return JsonResponse({"success": False, "error": "Unexpected API error."}, status=500)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
