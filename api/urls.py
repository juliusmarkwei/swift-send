from django.urls import path
from . import views

urlpatterns = [
    path('contact', views.ContactView.as_view(), name='contacts-view'),
    path('contact/<int:contactID>', views.ContactView.as_view(), name='contacts-view'),
    path('send-sms', views.SendSMSView.as_view(), name='send-sms-view'),
    path('message', views.MessageView.as_view(), name='message-view'),
    path('message/<int:messageID>', views.MessageView.as_view(), name='message-view'),
]
