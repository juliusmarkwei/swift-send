from django.contrib.auth import get_user_model
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog
from src.msg_templates.models import Template, ContactTemplate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
from rest_framework.permissions import IsAuthenticated
from .send_sms import send_sms
from .utils import (
    clean_contacts,
    create_message_logs,
    create_recipient_log,
    generate_personalized_message
)
from django.db import IntegrityError
from datetime import datetime
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


User = get_user_model
PAGE_SIZE = 10

class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    
    server_response = openapi.Response('response description', ContactSerializer)
    @swagger_auto_schema(
        operation_id='Get all contacts', operation_description='Get all contacts. Optionally, add query parameter(s) with keys:\
            phone=233xxxxxxxx | full_name=John Doe | ordering. Default PAGE SIZE is 10 and PAGE NUMBER is 1',
        responses={200: server_response, 401: 'Unauthorized'}, tags=['contacts'])
    def get(self, request):
        user = request.user
        ordering = request.query_params.get('ordering')
        
        contacts = Contact.objects.filter(created_by=user)
        
        # Filter by phone number if provided in query parameters
        phone_number = request.query_params.get('phone', None)
        if phone_number:
            formatted_phone_number = '+' + phone_number
            contacts = contacts.filter(phone=formatted_phone_number)
            
        # Filter by full_name if provided in query parameters
        full_name = request.query_params.get('full_name', None)
        if full_name:
            contacts = contacts.filter(full_name=full_name)
                  
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

    server_response = openapi.Response('response description', ContactCreateSerializer)
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'full_name': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
            'phone': openapi.Schema(type=openapi.TYPE_STRING),
            'info': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['phone', 'full_name',],
    ),
    responses={201: 'Created', 400: 'Bad Request'},
    operation_id='Create a contact',
    operation_description='Create a contact. Required field(s): phone, full_name',
    tags=['contacts']
    )
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
    
    parameters = openapi.Parameter('contactFullName', openapi.IN_PATH, description='Contact Full Name', type=openapi.TYPE_STRING)
    server_response = openapi.Response('response description', ContactSerializer)
    @swagger_auto_schema(operation_id='Get a contact', operation_description='Get a contact by their full name', manual_parameters=[parameters],
                         responses={200: server_response, 401: 'Unauthorized'}, tags=['contacts'])
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
    
    
    @swagger_auto_schema(operation_id='Update a contact', operation_description='Update a contact by their full name', manual_parameters=[parameters],
                         responses={200: server_response, 401: 'Unauthorized'}, request_body=ContactUpdateSerializer(), tags=['contacts'])
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
    
    
    @swagger_auto_schema(operation_id='Delete a contact', operation_description='Delete a contact by full name', manual_parameters=[parameters],
                         responses={204: 'No Content', 401: 'Unauthorized'}, tags=['contacts'])
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
    
    server_response = openapi.Response('response description', TemplateSerializer)
    @swagger_auto_schema(operation_id='Get all templates', operation_description='Get all templates. Optionally, add query parameter(s) with keys:\
        name=template_name | ordering. Default PAGE SIZE is 10 and PAGE NUMBER is 1',
                         responses={200: server_response,  401: 'Unauthorized'}, tags=['templates'])
    def get(self, request):
        user = request.user
        ordering = request.query_params.get('ordering')
        
        templates = Template.objects.filter(created_by=user)
        
        # Filter by name if provided in query parameters
        name = request.query_params.get('name', None)
        if name:
            templates = templates.filter(name=name)
            
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
    
    
    @swagger_auto_schema(operation_id='Create a template', operation_description='Create a template. Required field(s): name, content',
                         responses={201: 'Created',  401: 'Unauthorized'}, request_body=TemplateSerializer(), tags=['templates'])
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
    
    parameter = openapi.Parameter('templateName', openapi.IN_PATH, description='Template name', type=openapi.TYPE_STRING)
    server_response = openapi.Response('response description', TemplateSerializer)
    @swagger_auto_schema(operation_id='Get a template', operation_description="Get a template by it's name", manual_parameters=[parameter],
                         responses={200: server_response,  401: 'Unauthorized'}, tags=['templates'])
    def get(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response({'message': 'Template name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
            print('yesyyyyyyyyy')
            serializer = TemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(operation_id='Update a template', operation_description="Update a template by its name", manual_parameters=[parameter],
                         responses={200: server_response,  401: 'Unauthorized'}, request_body=TemplateUpdateSerializer(), tags=['templates'])
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
    
    
    @swagger_auto_schema(operation_id='Delete a template', operation_description="Delete a template by its name", manual_parameters=[parameter],
                         responses={204: 'No Content',  401: 'Unauthorized'}, tags=['templates'])
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
    
    parameter = openapi.Parameter('templateName', openapi.IN_PATH, description='Template name', type=openapi.TYPE_STRING)
    server_response = openapi.Response('response description', ContactSerializer)
    @swagger_auto_schema(operation_id='Get contacts associated with a template', operation_description='Get contacts associated with a template by template name',
                         manual_parameters=[parameter], responses={200: server_response,  401: 'Unauthorized'}, tags=['templates'])
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
        
    
    data = openapi.Schema(
    title='Contact data',
    type=openapi.TYPE_OBJECT,
    properties={
        'contacts': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='List of contact(s)'
        )
    },required=['contacts'])
    @swagger_auto_schema(operation_id='Add contacts to a template', operation_description='Add contacts to a template by template name. Note: Contact will be created if it does not exist in your contacts.',
        manual_parameters=[parameter], responses={201: 'Created',  401: 'Unauthorized'}, request_body=data, tags=['templates'])
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
        phoneNotInContacts = False
        phoneNotInContacts_list = []
        contactAlreadyIntemplateContacts = False
        contactAlreadyIntemplateContacts_list = []
        
        for recipient in recipient_lists:
            contact = None  # Initialize contact variable
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

    
    
    @swagger_auto_schema(operation_id='Remove contacts from a template', operation_description='Remove contacts from a template by template name',
                         manual_parameters=[parameter], responses={204: 'No Content',  401: 'Unauthorized'}, request_body=data, tags=['templates'])
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
    
    sever_response = openapi.Response('response description', MessageLogSerializer)
    @swagger_auto_schema(operation_id='Get all message logs', operation_description='Get all message logs. Optionally, add query parameter(s) with keys:\
        content=message_content | date=yyyy-mm-dd | ordering.',
                         responses={200: sever_response,  401: 'Unauthorized'}, tags=['message-logs'])
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
        
        serializer = MessageLogSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageLogDetailVIew(APIView):
    permission_classes = [IsAuthenticated]
    
    server_response = openapi.Response('response description', MessageLogDetailSerializer)
    @swagger_auto_schema(operation_id='Get a message log', operation_description='Get a message log by ID', manual_parameters=[openapi.Parameter('messageId', openapi.IN_PATH, description='Message ID', type=openapi.TYPE_INTEGER)],
                            responses={200: server_response,  401: 'Unauthorized'}, tags=['message-logs'])
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
    
    # resend an unedited log message, mssage goes to all associated contacts
    server_response = openapi.Response('response description', MessageLogSerializer)
    @swagger_auto_schema(operation_id='Resend a message log', operation_description='Resend a message log by ID. Message goes to all recent recipients',
                         manual_parameters=[openapi.Parameter('messageId', openapi.IN_PATH, description='Message ID', type=openapi.TYPE_INTEGER)],
                         responses={204: 'Message sent!', 401:'Unauthorized' }, tags=['message-logs'])
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
    @swagger_auto_schema(operation_id='Edit and resend a message log', operation_description='Edit and resend a message log by ID. Message goes to all recent recipients',
                         manual_parameters=[openapi.Parameter('messageId', openapi.IN_PATH, description='Message ID', type=openapi.TYPE_INTEGER)],
                         responses={204: 'Message updated and sent!', 401: 'Unauthorized'}, request_body=MessageLogUpdateSerializer(), tags=['message-logs'])
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
    
    data = openapi.Schema(
    title='Message data',
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Content of the message to be sent'
        ),
        'contacts': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
            description='List of contact(s)'
        )
    },
    required=['message', 'contacts']
    )
    @swagger_auto_schema(operation_id='Send a message', operation_description="Send a message to one or more contacts. Required field(s): message, contacts.\
        Note: Phone number(s) must be in your contacts and the format should be [\"+233xxxxxxxxxx\", \"+233xxxxxxxxxx\"]",
                         responses={204: 'No Content', 401: 'Unauthorized'}, request_body=data, tags=['send-message'])
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
    
    parameter = openapi.Parameter('templateName', openapi.IN_PATH, description='Template ID', type=openapi.TYPE_STRING)
    @swagger_auto_schema(operation_id='Send a template message', operation_description='Send a template message to all associated contacts',
                            manual_parameters=[parameter], responses={204: 'No Content', 401: 'Unauthorized'}, tags=['send-message-template'])
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
                print(personalized_message)
                print(contact.phone)
                response = send_sms(message=personalized_message, to=[contact.phone])
                print(response)
                messageLog = create_message_logs(message=personalized_message, user=user)
                print('yeayyyyyyyyyaaaas')
                create_recipient_log(messageLogInstance=messageLog, response=response, user=user)
                                
                template.last_sent = datetime.now()
                template.save()
            except Exception as e:
                return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Message sent!'}, status=status.HTTP_204_NO_CONTENT)

        
