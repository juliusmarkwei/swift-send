from django.urls import path
from . import views

urlpatterns = [
    path('contacts', views.ContactView.as_view(), name='contacts-view'),
    path('contacts/<int:contactId>', views.ContactView.as_view(), name='contacts-detail'),
    path('send-message', views.SendMessageView.as_view(), name='send-message'),
    path('message-logs', views.MessageLogView.as_view(), name='message-logs'),
    path('message-logs/<int:messageId>', views.MessageLogView.as_view(), name='mmessage-log-detail'),
    path('message-logs/<int:messageId>/resend', views.ResendLogMessgae.as_view(), name='resend-message'),
    path('templates', views.TemplateView.as_view(), name='template-view'),
    path('templates/<int:templateId>', views.TemplateView.as_view(), name='template-detail'),
    
]
