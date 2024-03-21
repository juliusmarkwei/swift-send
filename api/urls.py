from django.urls import path
from . import views

urlpatterns = [
    path('contact', views.ContactView.as_view(), name='contacts-view'),
    path('contact/<int:contactID>', views.ContactView.as_view(), name='contacts-view'),
    path('message', views.MessageView.as_view(), name='message-view'),
    path('message/<int:messageID>', views.MessageView.as_view(), name='message-view'),
    path('template', views.TemplateView.as_view(), name='template-view'),
    path('template/<int:templateID>', views.TemplateView.as_view(), name='template-view'),
]
