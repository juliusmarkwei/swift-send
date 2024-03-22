from django.contrib.auth import get_user_model
from contacts.models import Contact
from messages_logs.models import MessageLog
from msg_templates.models import Template, ContactTemplate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactSerializer, MessageLogSerializer, TemplateSerializer, MessageLogDetailSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .send_sms import send_sms
from .utils import clean_contacts, create_message_logs, save_new_contact
from django.db import IntegrityError



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
    


class TemplateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, templateID=None):
        user = request.user
        if templateID:
            try:
                template = Template.objects.get(pk=templateID, created_by=user)
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
              
                contacts = request_data.get('contacts', [])
                if contacts:
                    recipient_lists = clean_contacts(contacts)
                    for recipient in recipient_lists:
                        contact, created = Contact.objects.get_or_create(phone=recipient, created_by=user)
                        if created:
                            contact.save()
                        # Create association between contact and template
                        ContactTemplate.objects.create(contact=contact, template=template)

                # Check if sending SMS is requested
                distribute = request_data.get('distribute', False)
                if distribute:
                    if contacts:
                        try:
                            response = send_sms(message=template.content, to=recipient_lists)
                            create_message_logs(message=template.content, user=user, recipient_lists=recipient_lists, status='Sent')
                        except Exception as e:
                            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
                        return Response({'message': 'Message delivered!'}, status=status.HTTP_204_NO_CONTENT)
                    else:
                        return Response({'message': 'No contacts provided'}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
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

            contacts = request.data.get('contacts', [])
            if contacts:
                recipient_lists = clean_contacts(contacts)
                for recipient in recipient_lists:
                    try:
                        contact, created = Contact.objects.get_or_create(phone=recipient, created_by=user)
                        if created:
                            contact.save()
                        # Create association between contact and template
                        ContactTemplate.objects.get_or_create(contact=contact, template=template)
                    except IntegrityError:
                        pass                    
            # Check if sending SMS is requested
            distribute = request.data.get('distribute', False)
            if distribute:
                # Get associated contacts and call function to send SMS
                associated_contacts = ContactTemplate.objects.filter(template=template).values_list('contact', flat=True)
                if not associated_contacts:
                    return Response({'message': 'No contacts associated with template'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    associated_contacts = Contact.objects.filter(pk__in=associated_contacts)
                    recipient_lists = [contact.phone for contact in associated_contacts if contact.phone]
                    response = send_sms(message=template.content, to=recipient_lists)
                    create_message_logs(message=template.content, user=user, recipient_lists=recipient_lists, status='Sent')
                    return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
                except Exception as e:
                    return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
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
    
    # resend a log message without changing the content
    def post(self, request, messageId):
        user = request.user
        try:
            message = MessageLog.objects.filter(pk=messageId, author=user)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        message_id = message.id
        associated_contacts = RecipientLog.objects.filter(message=message_id).values_list('contact', flat=True)
        
        try:
            response = send_sms(message=message.content, to=associated_contacts)
            create_message_logs(message=message.content, user=user, recipient_lists=recipient_lists, status='Sent')
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    # edit before resending a log message
    def put(self, request, messageId):
        user = request.user
        try:
            message = MessageLog.objects.filter(pk=messageId, author=user)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MessageLogSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            associated_contacts = RecipientLog.objects.filter(message=message).values_list('contact', flat=True)
            try:
                response = send_sms(message=message.content, to=associated_contacts)
                create_message_logs(message=message.content, user=user, recipient_lists=recipient_lists, status='Sent')
                return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
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
            create_message_logs(message=message, user=user, recipient_lists=recipient_lists, status='Sent')
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
