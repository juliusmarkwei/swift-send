from django.urls import path
from . import views

urlpatterns = [
    path('contact', views.ContactView.as_view(), name='contacts-view'),
    path('contact/<int:contactID>', views.ContactView.as_view(), name='contacts-view'),
    path('send-sms', views.SendSMSView.as_view(), name='send-sms-view'),
]
