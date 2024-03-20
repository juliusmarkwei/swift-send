from django.contrib.auth import get_user_model
from contacts.models import Contact
from messages_center.models import Message
from msg_templates.models import Template
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactSerializer, MessageSerializer, TemplateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .send_sms import send_sms

User = get_user_model()

class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        contacts = Contact.objects.filter(created_by=user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        print(user)
        request_data = request.data.copy()
        request_data['created_by'] = User.objects.get(username=user).id
        serializer = ContactSerializer(data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, contactID):
        user = request.user
        try:
            user_contacts = Contact.objects.filter(created_by=user)
            contact = user_contacts.get(pk=contactID)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, contactID):
        user = request.user
        try:
            user_contact = Contact.objects.filter(created_by=user)
            contact = user_contact.get(pk=contactID)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class SendSMSView(APIView):
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.POST
        recipients = data['to']
        if ',' in recipients:
            recipients_list = [recipient.strip() for recipient in recipients.split(',')]
        elif ' ' in recipients:
            recipients_list = [recipient.strip() for recipient in recipients.split()]
        elif ';' in recipients:
            recipients_list = [recipient.strip() for recipient in recipients.split(';')]
        elif '\n' in recipients:
            recipients_list = [recipient.strip() for recipient in recipients.split('\n')]
        else:
            recipients_list = [recipients.strip()]
            
        message = data['message']
        print(recipients_list, message)
        
        send_sms(message=message, to=recipients_list)
        
        return Response({'message': 'Message delivered!'}, status=status.HTTP_204_NO_CONTENT)