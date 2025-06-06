from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import ManagePendingInviteView, MeView,UserProfileView,RequestOTPView,  CreateBusinessView,InviteStaffView, VerifyUnifiedOTPView,ListPendingInvitesView,ResendStaffInviteView,ListStaffView,UpdateStaffView,MyBusinessesView,SwitchBusinessView,DebugCacheView,CurrentBusinessView,BusinessDetailView,ListPlansView,CurrentSubscriptionView,SubscribeBusinessView,AuditLogListView,AllAuditLogsView,IndianStatesView, IndustryTypeListView, RegistrationTypeListView,ValidateGSTDetails, CheckSubscriptionStatusView, CreateTrialSubscriptionView, ReinviteStaffView

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('debug/', DebugCacheView.as_view()),
    path('auth/request-otp/', RequestOTPView.as_view()),
    path('auth/verify-otp/', VerifyUnifiedOTPView.as_view()),
    path('business/create/', CreateBusinessView.as_view()),
    path('business/<int:pk>/', BusinessDetailView.as_view(), name='business-detail'),
    path('invite-staff/', InviteStaffView.as_view(), name='invite-staff'),
    path('staff/', ListStaffView.as_view()),
    path("staff/invites/", ListPendingInvitesView.as_view()),
    path("staff/resend-invite/", ResendStaffInviteView.as_view()),
    path('staff/<int:user_id>/', UpdateStaffView.as_view()),
    path('staff/<int:user_id>/reinvite/', ReinviteStaffView.as_view(), name='reinvite-staff'),
    path("staff/pending/manage/", ManagePendingInviteView.as_view(), name="manage_pending_invite"),
    path('my-business/', MyBusinessesView.as_view()),
    path('switch-business/', SwitchBusinessView.as_view()),
    path('current-business/', CurrentBusinessView.as_view()),
    
    path('plans/', ListPlansView.as_view(), name='list-plans'),
    path('subscribe/', SubscribeBusinessView.as_view(), name='subscribe'),
    path('current-subscription/', CurrentSubscriptionView.as_view(), name='current-subscription'),
    path('check-subscription/', CheckSubscriptionStatusView.as_view(), name='check-subscription'),
    path('create-trial/', CreateTrialSubscriptionView.as_view(), name='create-trial'),
    
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs"),
    path("audit-logs/all/", AllAuditLogsView.as_view(), name="all_audit_logs"),
    path('indian-states/', IndianStatesView.as_view(), name='indian-states'),
    # path('business-types/', BusinessTypeListView.as_view(), name='business-types'),
    path('industry-types/', IndustryTypeListView.as_view(), name='industry-types'),
    path('registration-types/', RegistrationTypeListView.as_view(), name='registration-types'),
    
    path('validate-gst/<str:gstin>/', ValidateGSTDetails.as_view(), name='validate-gst-detail'),
]
