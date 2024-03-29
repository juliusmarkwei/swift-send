from django.urls import path
from . import views

urlpatterns = [
    path('contacts', views.ContactView.as_view(), name='contacts-view'),
    path('contacts/<str:contactFullName>', views.ContactDetailView.as_view(), name='contacts-detail'),
    path('send-message', views.SendMessageView.as_view(), name='send-message'),
    path('message-logs', views.MessageLogView.as_view(), name='message-logs'),
    path('message-logs/<int:messageId>', views.MessageLogDetailVIew.as_view(), name='mmessage-log-detail'),
    path('message-logs/<int:messageId>/resend', views.ResendLogMessgae.as_view(), name='resend-message'),
    path('templates', views.TemplateView.as_view(), name='template-view'),
    path('templates/<str:templateName>', views.TemplateDetailView.as_view(), name='template-detail'),
    path('templates/<str:templateName>/contacts', views.TemplateContactView.as_view(), name='template-contacts'),
    path('templates/<str:templateName>/send', views.SendTemplateMessage.as_view(), name='send-template'),
    
]
