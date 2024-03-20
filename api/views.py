from django.contrib.auth import get_user_model
from contacts.models import Contact
from messages_center.models import Message, ContactMessage
from msg_templates.models import Template
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactSerializer, MessageSerializer, TemplateSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .send_sms import send_sms
from .utils import clean_contacts


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
        message = data['message']
        recipients = data['to']
        recipients_list = clean_contacts(recipients)
        
        try:
            response = send_sms(message=message, to=recipients_list)
        except Exception as e:
            return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Message delivered!'}, status=status.HTTP_204_NO_CONTENT)
    
    
class MessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, messageID=None):
        user = request.user
        if messageID:
            try:
                message = Message.objects.get(pk=messageID, created_by=user)
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Message.DoesNotExist:
                return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            messages = Message.objects.filter(created_by=user)
            if not messages:
                return Response({'message': 'No messages found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            user = request.user
            request_data = request.data.copy()
            request_data['created_by'] = User.objects.get(username=user).id
            
            serializer = MessageSerializer(data=request_data)
           
            if serializer.is_valid():
                message = serializer.save()
              
                contacts = request_data.get('contacts', [])
                if contacts:
                    recipient_lists = clean_contacts(contacts)
                    try:
                        print(message)
                        response = send_sms(message=message, to=recipient_lists)
                        print('yayyyyyyyyyy')
                        contacts_objects = Contact.objects.filter(pk__in=contacts)
                        for contact in contacts_objects:
                            ContactMessage.objects.create(contact=contact, message=message)
                    except Exception as e:
                        return Response({'message': f'Error: {e}'}, status=status.HTTP_400_BAD_REQUEST)
                    return Response({'message': 'Message delivered!'}, status=status.HTTP_204_NO_CONTENT)
                    
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, messageID):
        user = request.user
        try:
            user_messages = Message.objects.filter(created_by=user)
            message = user_messages.get(pk=messageID)
        except Message.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, messageID):
        try:
            user = request.user
            user_message = Message.objects.filter(created_by=user)
            message = user_message.get(pk=messageID)
            message.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Message.DoesNotExist:
            return Response({'message': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
            if not templates:
                return Response({'message': 'No templates found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = TemplateSerializer(templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            user = request.user
            request_data = request.data.copy()
            request_data['created_by'] = User.objects.get(username=user).id
            serializer = TemplateSerializer(data=request_data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, templateID):
        user = request.user
        try:
            user_templates = Template.objects.filter(created_by=user)
            template = user_templates.get(pk=templateID)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TemplateSerializer(template, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, templateID):
        try:
            user = request.user
            user_template = Template.objects.filter(created_by=user)
            template = user_template.get(pk=templateID)
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Template.DoesNotExist:
            return Response({'message': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)