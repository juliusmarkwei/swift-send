from django.contrib.auth import get_user_model
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog
from src.msg_templates.models import Template, ContactTemplate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactSerializer, MessageLogSerializer, TemplateSerializer, MessageLogDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .send_sms import send_sms
from .utils import clean_contacts, create_message_logs, create_recipient_log
from django.db import IntegrityError
from datetime import datetime


User = get_user_model()

class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, contactId=None):
        user = request.user
        if contactId:
            try:
                contact = Contact.objects.get(pk=contactId, created_by=user)
                serializer = ContactSerializer(contact)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Contact.DoesNotExist:
                return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            contacts = Contact.objects.filter(created_by=user)
            serializer = ContactSerializer(contacts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        user = request.user
        request_data = request.data.copy()
        request_data['created_by'] = User.objects.get(username=user).id
        serializer = ContactSerializer(data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, contactId):
        user = request.user
        try:
            user_contacts = Contact.objects.filter(created_by=user)
            contact = user_contacts.get(pk=contactId)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, contactId):
        user = request.user
        try:
            contact = Contact.objects.filter(pk=contactId, created_by=user)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        contact.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class TemplateListCreateUpdateDestroyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, templateId=None):
        user = request.user
        if templateId:
            try:
                template = Template.objects.get(pk=templateId, created_by=user)
                serializer = TemplateSerializer(template)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Template.DoesNotExist:
                return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            templates = Template.objects.filter(created_by=user)
            serializer = TemplateSerializer(templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        try:
            user = request.user
            request_data = request.data.copy()
            request_data['created_by'] = User.objects.get(username=user).id
            
            serializer = TemplateSerializer(data=request_data)
           
            if serializer.is_valid():
                template = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def put(self, request, templateId):
        user = request.user
        try:
            user_templates = Template.objects.filter(created_by=user)
            template = user_templates.get(pk=templateId)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TemplateSerializer(template, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, templateId):
        try:
            user = request.user
            template = Template.objects.get(pk=templateId, created_by=user)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, templateId):
        user = request.user
        try:
            template = Template.objects.get(pk=templateId, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        contact_template_objects = ContactTemplate.objects.filter(template=template)
        contacts = Contact.objects.filter(pk__in=contact_template_objects.values_list('contact', flat=True))
        
        if contacts.exists():
            serializer = ContactSerializer(contacts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No contacts found for this template'}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, templateId):
        user = request.user
        try:
            template = Template.objects.get(pk=templateId, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        request_data = request.data.copy()
        contacts = request_data.get('contacts', [])
        if not contacts:
            return Response({'message': 'No contacts provided'}, status=status.HTTP_400_BAD_REQUEST)
        recipient_lists = clean_contacts(contacts)
        for recipient in recipient_lists:
            contact, created = Contact.objects.get_or_create(phone=recipient, created_by=user)
            if created:
                contact.save()
            try:
                contact_template = ContactTemplate.objects.get_or_create(template=template, contact=contact)
            except IntegrityError:
                return Response({'message': 'Contact already exists in the template'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Contacts added to template'}, status=status.HTTP_201_CREATED)


      
class MessageLogView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, messageId=None):
        user = request.user
        if messageId:
            try:
                message = MessageLog.objects.get(pk=messageId, author=user)
                serializer = MessageLogDetailSerializer(message)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except MessageLog.DoesNotExist:
                return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            messages = MessageLog.objects.filter(author=user)
            if not messages:
                return Response({'message': 'No messages found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = MessageLogSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)



class ResendLogMessgae(APIView):
    permission_classes = [IsAuthenticated]
    
    # resend an unedited log message, mssage goes to all associated contacts
    def post(self, request, messageId):
        user = request.user
        try:
            message = MessageLog.objects.get(pk=messageId, author=user)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        associated_contacts = RecipientLog.objects.filter(message=message)
        
        try:
            recipient_numbers = [contact.contact.phone for contact in associated_contacts]
            response = send_sms(message=message.content, to=recipient_numbers)
            messageId = create_message_logs(message=message.content, user=user)
            create_recipient_log(recipient_lists=recipient_numbers, messageLogInstace=messageId, response=response, user=user)
            
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    # edit and resend a message log
    def put(self, request, messageId):
        user = request.user
        try:
            original_message = MessageLog.objects.get(pk=messageId, author=user)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MessageLogSerializer(original_message, data=request.data, partial=True)
        if serializer.is_valid():
            # Create a new message log if the user edits the message
            new_message_log = serializer.save(author=user)
            
            # Send the edited message log to its associated users
            associated_contacts = RecipientLog.objects.filter(message=new_message_log)
            try:
                recipient_numbers = [contact.contact.phone for contact in associated_contacts]
                response = send_sms(message=new_message_log.content, to=recipient_numbers)
                messageId = create_message_logs(message=new_message_log.content, user=user)
                create_recipient_log(recipient_lists=recipient_numbers, messageLogInstace=messageId, response=response, user=user)
            
            except Exception as e:
                return Response({'message': f'Error sending message: {e}'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Message updated and sent!', 'new_message_id': new_message_log.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# view for sending a message to a single or multiple contacts
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        request_data = request.data.copy()
        message = request_data.get('message', None)
        contacts = request_data.get('contacts', [])
        if not message:
            return Response({'message': 'Message content not provided'}, status=status.HTTP_400_BAD_REQUEST)
        if not contacts:
            return Response({'message': 'No contacts provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipient_lists = clean_contacts(contacts)
        for recipient in recipient_lists:
            contact, created = Contact.objects.get_or_create(phone=recipient, created_by=user)
            if created:
                contact.save()
        
        try:
            response = send_sms(message=message, to=recipient_lists)
            messageLog =create_message_logs(message=message, user=user)
            create_recipient_log(recipient_lists=recipient_lists, messageLogInstace=messageLog, response=response, user=user)
            
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)


class SendTemplateMessage(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, templateId):
        user = request.user
        try:
            template = Template.objects.get(pk=templateId, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        contact = ContactTemplate.objects.filter(template=template).values_list('contact', flat=True)
        print(contact)
        if contact:
            recipient_lists = []
            for contact in contact:
                recipient_lists.append(Contact.objects.get(pk=contact).phone)
                
            try:
                response = send_sms(message=template.content, to=recipient_lists)
                messageLog = create_message_logs(message=template.content, user=user)
                create_recipient_log(recipient_lists=recipient_lists, messageLogInstace=messageLog, response=response, user=user)
                
                template.last_sent = datetime.now()
                template.save()
            except Exception as e:
                return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message': 'No contacts provided'}, status=status.HTTP_400_BAD_REQUEST)