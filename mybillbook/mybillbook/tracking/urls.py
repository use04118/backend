from django.urls import path
from .views import list_document_tracking,track_email_open

urlpatterns = [
    path('trackings/',list_document_tracking, name='list_document_tracking'),
    path('track-email-open', track_email_open, name='track-email-open'),
]
