from users.models import Business, Role,User,SubscriptionPlan,Subscription,AuditLog,StaffInvite
from users.utils import get_current_business
from rest_framework import permissions
from datetime import timedelta
from django.utils import timezone

# class HasSalesPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         business = get_current_business(user)

#         if not business:
#             return False

#         role = Role.objects.filter(user=user, business=business).first()
#         if not role:
#             return False

#         # ✅ Wildcard admin shortcut
#         if "*" in role.permissions and role.permissions["*"]:
#             return True
        
#         if role.role_name == 'partner' :
#             return True

#         method = view.request.method
#         permission_key = None

#         if method in ['GET']:
#             permission_key = 'sales.view'
#         elif method in ['POST']:
#             permission_key = 'sales.create'
#         elif method in [ 'PUT', 'PATCH']:
#             permission_key = 'sales.edit'
#         elif method == 'DELETE':
#             permission_key = 'sales.delete'

#         return role.permissions.get(permission_key, False)

# class HasCreditNotePermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         business = get_current_business(user)

#         if not business:
#             return False

#         role = Role.objects.filter(user=user, business=business).first()
#         if not role:
#             return False

#         # ✅ Wildcard admin shortcut
#         if "*" in role.permissions and role.permissions["*"]:
#             return True
        
#         if role.role_name == 'partner' :
#             return True

#         method = view.request.method
#         permission_key = None

#         if method in ['GET']:
#             permission_key = 'creditnote.view'
#         elif method in ['POST']:
#             permission_key = 'creditnote.create'
#         elif method in [ 'PUT', 'PATCH']:
#             permission_key = 'creditnote.edit'
#         elif method == 'DELETE':
#             permission_key = 'creditnote.delete'

#         return role.permissions.get(permission_key, False)

# class HasSalesReturnPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         business = get_current_business(user)

#         if not business:
#             return False

#         role = Role.objects.filter(user=user, business=business).first()
#         if not role:
#             return False

#         # ✅ Wildcard admin shortcut
#         if "*" in role.permissions and role.permissions["*"]:
#             return True
        
#         if role.role_name == 'partner' :
#             return True

#         method = view.request.method
#         permission_key = None

#         if method in ['GET']:
#             permission_key = 'salesreturn.view'
#         elif method in ['POST']:
#             permission_key = 'salesreturn.create'
#         elif method in [ 'PUT', 'PATCH']:
#             permission_key = 'salesreturn.edit'
#         elif method == 'DELETE':
#             permission_key = 'salesreturn.delete'

#         return role.permissions.get(permission_key, False)


class HasSalesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        business = get_current_business(user)

        if not business:
            return False

        role = Role.objects.filter(user=user, business=business).first()
        if not role or not role.permissions:
            return False

        permissions = role.permissions

        # ✅ Wildcard admin shortcut
        if permissions.get("*"):
            return True

        method = view.request.method
        category = "sales"
        action = None

        if method == 'GET':
            action = 'view'
        elif method in ['POST', 'PUT', 'PATCH']:
            action = 'create'
        elif method == 'DELETE':
            action = 'delete'

        if not action:
            return False

        category_perms = permissions.get(category, {})

        # ✅ Check for category wildcard or specific action
        if category_perms.get("*") or category_perms.get(action):
            return True

        return False
