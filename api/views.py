from django.contrib.auth import get_user_model
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog
from src.msg_templates.models import Template, ContactTemplate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

from django.db import IntegrityError
from datetime import datetime
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema_field,
)
from drf_spectacular.types import OpenApiTypes

from .send_sms import send_sms
from .serializers import (
    ContactSerializer,
    MessageLogSerializer,
    TemplateSerializer,
    MessageLogDetailSerializer,
    ContactUpdateSerializer,
    TemplateUpdateSerializer,
    ContactCreateSerializer,
    TemplateCreateSerializer,
    ResendEditedMessageLogSerializer,
    SendMessageSerializer,
    ContactBodySerializer,
    TemplateBodySerializer,
)
from .utils import (
    clean_contacts,
    create_message_logs,
    create_recipient_log,
    generate_personalized_message,
)


User = get_user_model
PAGE_SIZE = 10


class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = (MultiPartParser, FormParser, FileUploadParser, )

    parameters = [
        OpenApiParameter(
            name="phone",
            description="Phone number",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="ordering",
            description="Order response by field",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="page",
            description="Page number",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
    ]

    @extend_schema(
        operation_id="get all contacts",
        summary="list all contacts",
        parameters=parameters,
        tags=["contacts"],
        responses=ContactSerializer,
        request=None,
    )
    @method_decorator(cache_page(20))  # 20 seconds
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request):
        user = request.user
        ordering = request.query_params.get("ordering")

        contacts = Contact.objects.filter(created_by=user)

        # Filter by phone number if provided in query parameters
        phone_number = request.query_params.get("phone", None)
        if phone_number:
            formatted_phone_number = "+" + phone_number
            contacts = contacts.filter(phone=formatted_phone_number)

        # Ordering by field if provided in query parameters
        if ordering:
            contacts = contacts.order_by(ordering)

        page_number = request.query_params.get("page", 1)
        paginator = Paginator(contacts, PAGE_SIZE)

        try:
            contacts_page = paginator.page(page_number)
        except EmptyPage:
            return Response(
                {"message": "Requested page does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ContactSerializer(contacts_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=(ContactSerializer),
        responses={201: ContactSerializer},
        summary="Create a contact",
        description="Create a contact. Required field(s): phone, full_name. Format for phone should start with country code: +233xxxxxxxxxx",
        tags=["contacts"],
    )
    def post(self, request):
        user = request.user
        request_data = request.data.copy()

        request_data["created_by"] = user.id

        # Check if a contact with the same phone number and user already exists
        existing_contact = Contact.objects.filter(
            phone=request_data["phone"], created_by=user
        ).exists()
        if existing_contact:
            return Response(
                {"message": "Contact already exist"}, status=status.HTTP_409_CONFLICT
            )

        serializer = ContactCreateSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactDetailView(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    parameters = [
        OpenApiParameter(
            name="contactFullName",
            location=OpenApiParameter.PATH,
            description="Contact Full Name",
            type=OpenApiTypes.STR,
        )
    ]
    response = OpenApiResponse(
        description="Response description",
        response=ContactSerializer,  # Assuming ContactSerializer is your serializer class
    )

    @extend_schema(
        summary="Get a contact",
        description="Get a contact by specifying their full name",
        parameters=parameters,
        request=None,
        responses=ContactSerializer,
        tags=["contacts"],
    )
    def get(self, request, contactFullName=None):
        user = request.user
        try:
            if contactFullName is None:
                return Response(
                    {"message": "Contact's full name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            formattedFulName = contactFullName.strip()
            contact = Contact.objects.get(full_name=formattedFulName, created_by=user)
            serializer = ContactSerializer(contact)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Contact.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Update a contact",
        description="Update a contact by specifying their full name",
        parameters=parameters,
        responses=ContactUpdateSerializer,
        request=ContactUpdateSerializer,
        tags=["contacts"],
    )
    def put(self, request, contactFullName=None):
        user = request.user
        try:
            if contactFullName is None:
                return Response(
                    {"message": "Contact full name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_contacts = Contact.objects.filter(created_by=user)
            formattedFulName = contactFullName.strip()
            contact = user_contacts.get(full_name=formattedFulName)
        except Contact.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a contact",
        description="Delete a contact by specifying their full name",
        parameters=parameters,
        tags=["contacts"],
    )
    def delete(self, request, contactFullName=None):
        user = request.user
        try:
            if not contactFullName:
                return Response(
                    {"message": "Contact full name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            formattedFullName = contactFullName.strip()
            contact = Contact.objects.get(full_name=formattedFullName, created_by=user)
            contact.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contact.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    # parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    paramters = [
        OpenApiParameter(
            name="ordering",
            description="Order response by field",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="page",
            description="Page number",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
    ]

    @extend_schema(
        summary="List all templates",
        description="List all templates created by current user",
        parameters=paramters,
        request=None,
        tags=["templates"],
        responses={200: TemplateSerializer},
    )
    @method_decorator(cache_page(20))  # 20 seconds
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request):
        user = request.user
        ordering = request.query_params.get("ordering")

        templates = Template.objects.filter(created_by=user)

        # Ordering by field if provided in query parameters
        if ordering:
            templates = templates.order_by(ordering)

        page_number = request.query_params.get("page", 1)
        paginator = Paginator(templates, PAGE_SIZE)
        try:
            templates_page = paginator.page(page_number)
        except EmptyPage:
            return Response(
                {"message": "Requested page does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TemplateSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a template",
        description="Create a template. Add contact's fields like <full_name> to personalze message",
        tags=["templates"],
        request=TemplateBodySerializer(),
    )
    def post(self, request):
        try:
            user = request.user
            request_data = request.data.copy()
            request_data["created_by"] = user.id

            if not request_data.get("name") or not request_data.get("content"):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            template_name_exists = Template.objects.filter(
                name=request_data["name"], created_by=user
            ).exists()
            if template_name_exists:
                return Response(
                    {"message": "Template name already exist, choose a different name"},
                    status=status.HTTP_409_CONFLICT,
                )
            serializer = TemplateCreateSerializer(data=request_data)

            if serializer.is_valid():
                template = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"message": "An error occured, try again!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {"message": "Template created successfully!"},
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class TemplateDetailView(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    parameters = [
        OpenApiParameter(
            name="templateName",
            location=OpenApiParameter.PATH,
            description="Template Name",
            type=OpenApiTypes.STR,
        )
    ]

    @extend_schema(
        summary="Get a template",
        description="Get a template by specifying its name",
        parameters=parameters,
        responses={200: TemplateSerializer},
        request=None,
        tags=["templates"],
    )
    def get(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response(
                    {"message": "Template name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
            serializer = TemplateSerializer(template)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Template.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Update a template",
        description="Update a template by specifying its name",
        parameters=parameters,
        responses={200: TemplateUpdateSerializer},
        request=TemplateUpdateSerializer,
        tags=["templates"],
    )
    def put(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response(
                    {"message": "Template name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_templates = Template.objects.filter(created_by=user)
            formattedTemplateName = templateName.strip()
            template = user_templates.get(name=formattedTemplateName)
        except Template.DoesNotExist:
            return Response(
                {"message": "Template does not exist!"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TemplateUpdateSerializer(template, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"message": "Bad request, try again!"}, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Delete a template",
        description="Delete a template by specifying its name",
        parameters=parameters,
        request=None,
        responses=None,
        tags=["templates"],
    )
    def delete(self, request, templateName=None):
        try:
            if templateName is None:
                return Response(
                    {"message": "Template name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = request.user
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Template.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateContactView(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    parameters = [
        OpenApiParameter(
            name="templateName",
            location=OpenApiParameter.PATH,
            description="Template Name",
            type=OpenApiTypes.STR,
        )
    ]

    @extend_schema(
        summary="Get contacts associated with a template",
        description="Get contacts associated with a template by specifying template name",
        parameters=parameters,
        request=None,
        tags=["template-contacts"],
    )
    def get(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response(
                    {"message": "Template name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        contact_template_objects = ContactTemplate.objects.filter(template_id=template)
        contacts = Contact.objects.filter(
            pk__in=contact_template_objects.values_list("contact_id", flat=True)
        )

        if contacts.exists():
            serializer = ContactSerializer(contacts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Associate contacts with a template",
        description='Add a list of contacts to associate with a template, format: ["+233xxxxxxxxx", ...]. Specify the template name.',
        request=ContactBodySerializer(),
        tags=["template-contacts"],
    )
    def post(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response(
                    {"message": "Template name not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response(
                {"message": "Template not found"}, status=status.HTTP_404_NOT_FOUND
            )

        request_data = request.data.copy()
        contacts = request_data.get("contacts", [])
        if not contacts:
            return Response(
                {"message": "No contacts provided"}, status=status.HTTP_400_BAD_REQUEST
            )

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
                    contact_template, created = ContactTemplate.objects.get_or_create(
                        template_id=template, contact_id=contact
                    )
                    if not created:
                        contactAlreadyIntemplateContacts = True
                        contactAlreadyIntemplateContacts_list.append(recipient)
                except IntegrityError:
                    return Response(
                        {"message": "Integrity error occurred"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        if contactAlreadyIntemplateContacts and phoneNotInContacts:
            return Response(
                {
                    "message": f"Phone number(s) {contactAlreadyIntemplateContacts_list} already associated with template and {phoneNotInContacts_list} not in your contacts"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if phoneNotInContacts:
            return Response(
                {
                    "message": f"Phone number(s) {phoneNotInContacts_list} not in your contacts, try saving them first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if contactAlreadyIntemplateContacts:
            return Response(
                {
                    "message": f"Phone number(s) {contactAlreadyIntemplateContacts_list} already associated with template"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Contact(s) added to template"}, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Remove contact(s) from a template",
        description='Remove a list of contacts from a template. Format: ["+233xxxxxxxxx", ...]. Specify the template name.\
        For some wierd reason, the contacts request body required to perform this operation doesn\'t show, try using a different client.',
        request=ContactBodySerializer(),
        tags=["template-contacts"],
    )
    def delete(self, request, templateName=None, *args, **kwargs):
        user = request.user

        contacts = request.data.get("contacts", [])
        if len(contacts) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            if templateName is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        recipient_lists = clean_contacts(contacts)
        for recipient in recipient_lists:
            try:
                contact_template = ContactTemplate.objects.get(
                    template_id=template, contact_id__phone=recipient
                )
                contact_template.delete()
            except ContactTemplate.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageLogView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    parameters = [
        OpenApiParameter(
            name="ordering",
            description="Order response by field",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="content",
            description="Message content",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="page",
            description="Page number",
            location=OpenApiParameter.QUERY,
            required=False,
            type=OpenApiTypes.STR,
        ),
    ]

    @extend_schema(
        operation_id="get all message logs",
        summary="list all message logs",
        parameters=parameters,
        tags=["message_logs"],
        request=None,
        responses=MessageLogSerializer,
    )
    @method_decorator(cache_page(20))  # 20 seconds
    @method_decorator(vary_on_headers("Authorization"))
    def get(self, request):
        user = request.user
        ordering = request.query_params.get("ordering")

        messages = MessageLog.objects.filter(author_id=user)
        if not messages:
            return Response([], status=status.HTTP_404_NOT_FOUND)

        # Filter by message content if provided in query parameters
        content = request.query_params.get("content", None)
        if content:
            messages = messages.filter(content=content.strip())

        # Ordering by sent_date if provided in query parameters
        if ordering:
            messages = messages.order_by(ordering)

        page_number = request.query_params.get("page", 1)
        paginator = Paginator(messages, PAGE_SIZE)

        try:
            contacts_page = paginator.page(page_number)
        except EmptyPage:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = MessageLogSerializer(contacts_page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageLogDetailVIew(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    parameters = [
        OpenApiParameter(
            name="messageId",
            location=OpenApiParameter.PATH,
            description="Message ID",
            type=OpenApiTypes.INT,
        )
    ]

    @extend_schema(
        summary="Get a message log",
        description="Get a message log by specifying its ID",
        parameters=parameters,
        request=None,
        responses={200: MessageLogDetailSerializer},
        tags=["message_logs"],
    )
    def get(self, request, messageId=None):
        user = request.user
        try:
            if messageId is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            message = MessageLog.objects.get(pk=messageId, author_id=user)

            serializer = MessageLogDetailSerializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MessageLog.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ResendLogMessage(APIView):
    permission_classes = [IsAuthenticated]
    # throttle_classes = [UserRateThrottle]
    # parser_classes = [MultiPartParser, FormParser]

    # resend an unedited log message, mssage goes to all associated contacts
    parameters = [
        OpenApiParameter(
            name="messageId",
            location=OpenApiParameter.PATH,
            description="Message ID",
            type=OpenApiTypes.INT,
        )
    ]

    @extend_schema(
        summary="Resend a message log",
        description="Resend a message log by specifying its Id",
        parameters=parameters,
        request=None,
        tags=["message_logs"],
    )
    def post(self, request, messageId=None):
        user = request.user
        try:
            if messageId is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            message = MessageLog.objects.get(pk=messageId, author_id=user)
        except MessageLog.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        associated_contacts = RecipientLog.objects.filter(message_id=message).exclude(
            contact_id=None
        )

        try:
            recipient_numbers = [
                contact.contact_id.phone
                for contact in associated_contacts
                if contact.contact_id
            ]
            if not recipient_numbers:
                return Response(
                    {"message": "No contacts associated with message"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            response = send_sms(message=message.content, to=recipient_numbers)
            messageId = create_message_logs(message=message.content, user=user)
            create_recipient_log(
                messageLogInstance=messageId, response=response, user=user
            )

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class EditResendLogMessage(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Edit and resend message log",
        description="Edit and resend a message log by specifying its Id",
        request=ResendEditedMessageLogSerializer(),
        tags=["message_logs"],
    )
    def post(self, request, messageId=None):
        user = request.user
        try:
            if messageId is None:
                return Response(
                    {"message": "Message ID not provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            original_message = MessageLog.objects.get(pk=messageId, author_id=user)
        except MessageLog.DoesNotExist:
            return Response(
                {"message": "Message not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if request.data.get("content") is None or request.data.get("content") == "":
            return Response(
                {"message": "Message content not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        message_content = request.data.get("content")
        associated_contacts = RecipientLog.objects.filter(message_id=original_message)
        try:
            recipient_numbers = [
                contact.contact_id.phone
                for contact in associated_contacts
                if contact.contact_id
            ]
            if not recipient_numbers:
                return Response(
                    {"message": "Message contact(s) could be deleted!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            response = send_sms(message=message_content, to=recipient_numbers)
            messageId = create_message_logs(message=message_content, user=user)
            create_recipient_log(
                messageLogInstance=messageId, response=response, user=user
            )

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# view for sending a message to a one or multiple contacts
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    # parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Send a quick message",
        description="Send a quick message to one or more contacts. Contact(s) must be a list",
        request=SendMessageSerializer(),
        responses=None,
        tags=["send-message"],
    )
    def post(self, request):
        user = request.user
        request_data = request.data.copy()
        message = request_data.get("message", None)
        contacts = request_data.get("contacts", [])
        if not message or not contacts:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipient_lists = clean_contacts(contacts)
        phone_numbers = []
        for recipient in recipient_lists:
            try:
                contact = Contact.objects.get(phone=recipient, created_by=user)
                phone_numbers.append(contact.phone)
            except Contact.DoesNotExist:
                return Response(
                    {
                        "message": f"Contact with phone number {recipient} not found in your contacts"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        try:
            if not phone_numbers:
                return Response(
                    {"message": "No contacts found"}, status=status.HTTP_404_NOT_FOUND
                )
            response = send_sms(message=message, to=phone_numbers)
            messageLog = create_message_logs(message=message, user=user)
            create_recipient_log(
                messageLogInstance=messageLog, response=response, user=user
            )

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SendTemplateMessage(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    parser_classes = [MultiPartParser, FormParser]

    parameters = [
        OpenApiParameter(
            name="templateName",
            location=OpenApiParameter.PATH,
            description="Template Name",
            type=OpenApiTypes.STR,
        )
    ]

    @extend_schema(
        summary="Send a message using a template",
        description="Send a message using a template by specifying its name",
        parameters=parameters,
        request=None,
        tags=["send-message-template"],
    )
    def post(self, request, templateName=None):
        user = request.user
        try:
            if templateName is None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            formattedTemplateName = templateName.strip()
            template = Template.objects.get(name=formattedTemplateName, created_by=user)
        except Template.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        contacts = ContactTemplate.objects.filter(template_id=template)
        if len(contacts) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        for contact_template in contacts:
            contact = contact_template.contact_id
            try:
                template_content = template.content
                personalized_message = generate_personalized_message(
                    template_message=template_content, contact=contact
                )
                response = send_sms(message=personalized_message, to=[contact.phone])
                messageLog = create_message_logs(
                    message=personalized_message, user=user
                )
                create_recipient_log(
                    messageLogInstance=messageLog, response=response, user=user
                )

                template.last_sent = datetime.now()
                template.save()
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
