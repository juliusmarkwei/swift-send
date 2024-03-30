from django.contrib.auth import get_user_model
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog
from src.msg_templates.models import Template, ContactTemplate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle

from django.db import IntegrityError
from datetime import datetime
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from .send_sms import send_sms
from .serializers import (
    ContactSerializer,
    MessageLogSerializer,
    TemplateSerializer,
    MessageLogDetailSerializer,
    ContactUpdateSerializer,
    TemplateUpdateSerializer,
    MessageLogUpdateSerializer,
    ContactCreateSerializer,
    TemplateCreateSerializer,
)
from .utils import (
    clean_contacts,
    create_message_logs,
    create_recipient_log,
    generate_personalized_message
)


User = get_user_model
PAGE_SIZE = 10

class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 60))
    @method_decorator(vary_on_headers('Authorization'))
    def get(self, request):
        user = request.user
        ordering = request.query_params.get('ordering')
        
        contacts = Contact.objects.filter(created_by=user)
        
        # Filter by phone number if provided in query parameters
        phone_number = request.query_params.get('phone', None)
        if phone_number:
            formatted_phone_number = '+' + phone_number
            contacts = contacts.filter(phone=formatted_phone_number)
                  
        # Ordering by field if provided in query parameters
        if ordering:
            contacts = contacts.order_by(ordering)
        
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(contacts, PAGE_SIZE)
        
        try:
            contacts_page = paginator.page(page_number)
        except EmptyPage:
            return Response({'message': 'Requested page does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ContactSerializer(contacts_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        user = request.user
        request_data = request.data.copy()
        
        request_data['created_by'] = user.id
        
        # Check if a contact with the same phone number and user already exists
        existing_contact = Contact.objects.filter(phone=request_data['phone'], created_by=user).exists()
        if existing_contact:
            return Response({'message': 'Contact already exist'}, status=status.HTTP_409_CONFLICT)
        
        # print(request_data)
        serializer = ContactCreateSerializer(data=request_data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ContactDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, contactFullName=None):
        user = request.user
        try:
            if contactFullName is None:
                return Response({'message': 'Contact full name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedFulName = contactFullName.strip()
            contact = Contact.objects.get(full_name=formattedFulName, created_by=user)
            serializer = ContactSerializer(contact)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
    
 
    def put(self, request, contactFullName=None):
        user = request.user
        try:
            if contactFullName is None:
                return Response({'message': 'Contact full name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            user_contacts = Contact.objects.filter(created_by=user)
            formattedFulName = contactFullName.strip()
            contact = user_contacts.get(full_name=formattedFulName)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({'message': 'Contact with this number already exist!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, contactFullName=None):
        user = request.user
        try:
            if contactFullName is None:
                return Response({'message': 'Contact full name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedFulName = contactFullName.strip()
            contact = Contact.objects.get(full_name=formattedFulName, created_by=user)
            contact.delete()
            return Response({'message': 'Contact deleted!'}, status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)



class TemplateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    @method_decorator(cache_page(60 * 60))
    @method_decorator(vary_on_headers('Authorization'))
    def get(self, request):
        user = request.user
        ordering = request.query_params.get('ordering')
        
        templates = Template.objects.filter(created_by=user)
            
        # Ordering by field if provided in query parameters
        if ordering:
            templates = templates.order_by(ordering)
        
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(templates, PAGE_SIZE)
        try:
            templates_page = paginator.page(page_number)
        except EmptyPage:
            return Response({'message': 'Requested page does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def post(self, request):
        try:
            user = request.user
            request_data = request.data.copy()
            request_data['created_by'] = user.id
            
            template_name_exists = Template.objects.filter(name=request_data['name'], created_by=user).exists()
            if template_name_exists:
                return Response({'message': 'Template name already exist, choose a different name'}, status=status.HTTP_409_CONFLICT)
            serializer = TemplateCreateSerializer(data=request_data)
           
            if serializer.is_valid():
                template = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    
class TemplateDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
            serializer = TemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def put(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            user_templates = Template.objects.filter(created_by=user)
            formattedTemplateName = templateName.strip()
            template = user_templates.get(name=formattedTemplateName)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TemplateSerializer(template, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, templateName=None):
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

class TemplateContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        contact_template_objects = ContactTemplate.objects.filter(template_id=template)
        contacts = Contact.objects.filter(pk__in=contact_template_objects.values_list('contact_id', flat=True))
        
        if contacts.exists():
            serializer = ContactSerializer(contacts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No contacts found for this template'}, status=status.HTTP_404_NOT_FOUND)
        
    
    def post(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        request_data = request.data.copy()
        contacts = request_data.get('contacts', [])
        if not contacts:
            return Response({'message': 'No contacts provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipient_lists = clean_contacts(contacts)
        phoneNotInContacts, contactAlreadyIntemplateContacts = False, False
        phoneNotInContacts_list, contactAlreadyIntemplateContacts_list = [], []
        
        for recipient in recipient_lists:
            contact = None
            try:
                contact = Contact.objects.get(phone=recipient, created_by=user)
            except Contact.DoesNotExist:
                phoneNotInContacts = True
                phoneNotInContacts_list.append(recipient)
            
            if contact:
                try:
                    contact_template, created = ContactTemplate.objects.get_or_create(template_id=template, contact_id=contact)
                    if not created:
                        contactAlreadyIntemplateContacts = True
                        contactAlreadyIntemplateContacts_list.append(recipient)
                except IntegrityError:
                    return Response({'message': 'Integrity error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if contactAlreadyIntemplateContacts and phoneNotInContacts:
            return Response({'message': f'Phone number(s) {contactAlreadyIntemplateContacts_list} already associated with template and {phoneNotInContacts_list} not in your contacts'}, status=status.HTTP_400_BAD_REQUEST)
        if phoneNotInContacts:
            return Response({'message': f'Phone number(s) {phoneNotInContacts_list} not in your contacts, try saving them first.'}, status=status.HTTP_400_BAD_REQUEST)
        if contactAlreadyIntemplateContacts:
            return Response({'message': f'Phone number(s) {contactAlreadyIntemplateContacts_list} already associated with template'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Contact(s) added to template'}, status=status.HTTP_201_CREATED)

    
    def delete(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        contacts = request.data.get('contacts')
        if not contacts:
            return Response({'message': 'No contacts provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipient_lists = clean_contacts(contacts)
        with transaction.atomic():
            for recipient in recipient_lists:
                try:
                    contact_template = ContactTemplate.objects.get(template_id=template, contact_id__phone=recipient)
                except ContactTemplate.DoesNotExist:
                    return Response({'message': f'Contact {recipient} not found in the template'}, status=status.HTTP_404_NOT_FOUND)
                
                contact_template.delete()
        return Response({'message': 'Contacts removed from template'}, status=status.HTTP_204_NO_CONTENT)
                

  
class MessageLogView(APIView):
    permission_classes = [IsAuthenticated]
    
    @method_decorator(cache_page(60 * 60))
    @method_decorator(vary_on_headers('Authorization'))
    def get(self, request):
        user = request.user
        ordering = request.query_params.get('ordering')
        
        messages = MessageLog.objects.filter(author_id=user)
        if not messages:
            return Response([], status=status.HTTP_404_NOT_FOUND)
        
        # Filter by message content if provided in query parameters
        content = request.query_params.get('content', None)
        if content:
            messages = messages.filter(content=content.strip())
            
        # Filter by date if provided in query parameters
        date = request.query_params.get('date', None)
        if date:
            messages = messages.filter(sent_at__date=date)
        
        # Ordering by sent_date if provided in query parameters
        if ordering:
            messages = messages.order_by(ordering)
            
        page_number = request.query_params.get('page', 1)
        paginator = Paginator(messages, PAGE_SIZE)
        
        try:
            contacts_page = paginator.page(page_number)
        except EmptyPage:
            return Response({'message': 'Requested page does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MessageLogSerializer(contacts_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class MessageLogDetailVIew(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, messageId=None):
        user = request.user
        try:
            if messageId is None:
                return Response({'message': 'Message ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
            message = MessageLog.objects.get(pk=messageId, author_id=user)
            
            serializer = MessageLogDetailSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)



class ResendLogMessgae(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    # resend an unedited log message, mssage goes to all associated contacts
    def post(self, request, messageId=None):
        user = request.user
        try:
            if messageId is None:
                return Response({'message': 'Message ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
            message = MessageLog.objects.get(pk=messageId, author_id=user)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        associated_contacts = RecipientLog.objects.filter(message_id=message).exclude(contact_id=None)
        
        try:
            recipient_numbers = [contact.contact_id.phone for contact in associated_contacts if contact.contact_id]
            if not recipient_numbers:
                return Response({'message': 'No contacts associated with message'}, status=status.HTTP_400_BAD_REQUEST)
            response = send_sms(message=message.content, to=recipient_numbers)
            messageId = create_message_logs(message=message.content, user=user)
            create_recipient_log(messageLogInstance=messageId, response=response, user=user)
            
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)



    # edit and resend a message log
    def put(self, request, messageId=None):
        user = request.user
        try:
            if messageId is None:
                return Response({'message': 'Message ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
            original_message = MessageLog.objects.get(pk=messageId, author_id=user)
        except MessageLog.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.data.get('content') is None or request.data.get('content') == '':
            return Response({'message': 'Message content not provided'}, status=status.HTTP_400_BAD_REQUEST)
        message_content = request.data.get('content')
        # Send the edited message log to its associated users
        associated_contacts = RecipientLog.objects.filter(message_id=original_message)
        try:
            recipient_numbers = [contact.contact_id.phone for contact in associated_contacts if contact.contact_id]
            if not recipient_numbers:
                return Response({'message': 'No contacts associated with message'}, status=status.HTTP_400_BAD_REQUEST)
            response = send_sms(message=message_content, to=recipient_numbers)
            messageId = create_message_logs(message=message_content, user=user)
            create_recipient_log(messageLogInstance=messageId, response=response, user=user)
        
        except Exception as e:
            return Response({'message': f'Error sending message: {e}'}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message': 'Message updated and sent!'}, status=status.HTTP_204_NO_CONTENT)
    
    

# view for sending a message to a single or multiple contacts
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
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
        phone_numbers = []
        for recipient in recipient_lists:
            try:
                contact = Contact.objects.get(phone=recipient, created_by=user)
                phone_numbers.append(contact.phone)
            except Contact.DoesNotExist:
                return Response({'message': f'Contact with phone number {recipient} not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            if not phone_numbers:
                return Response({'message': 'No contacts found'}, status=status.HTTP_404_NOT_FOUND)
            response = send_sms(message=message, to=phone_numbers)
            messageLog =create_message_logs(message=message, user=user)
            create_recipient_log(messageLogInstance=messageLog, response=response, user=user)
            
            return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)



class SendTemplateMessage(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def post(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        contacts = ContactTemplate.objects.filter(template_id=template)
        for contact_template in contacts:
            contact = contact_template.contact_id
            try:
                template_content = template.content
                personalized_message = generate_personalized_message(template_message=template_content, contact=contact)
                response = send_sms(message=personalized_message, to=[contact.phone])
                messageLog = create_message_logs(message=personalized_message, user=user)
                create_recipient_log(messageLogInstance=messageLog, response=response, user=user)
                                
                template.last_sent = datetime.now()
                template.save()
            except Exception as e:
                return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)
