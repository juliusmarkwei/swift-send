from src.accounts.models import UserAccount
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog
from src.msg_templates.models import Template
from rest_framework import serializers
from django.contrib.auth.hashers import make_password



class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'created_at', 'updated_at']
        
  

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'info', 'created_at', 'updated_at']

class ContactUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    info = serializers.CharField(required=False)
    
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'middle_name', 'email', 'phone', 'info']

class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'info']
        
class RecipientLogSerializer(serializers.ModelSerializer):
    contact_details = ContactDetailSerializer(source='contact', read_only=True)
    
    class Meta:
        model = RecipientLog
        fields = ['id', 'contact_details']
        
              
class MessageLogDetailSerializer(serializers.ModelSerializer):
    recipients = RecipientLogSerializer(source='recipientlog_set', many=True, read_only=True)
    
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_at', 'recipients']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

class MessageLogSerializer(serializers.ModelSerializer):
    recipients = RecipientLogSerializer(source='recipientlog_set', many=True, read_only=True)
    
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_at', 'recipients']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Customizing the format of recipients data
        formatted_recipients = []
        for recipient in data['recipients']:
            recipient_data = {
                'contact_id': recipient['contact_details']['id'],}
            formatted_recipients.append(recipient_data)
        data['recipients'] = formatted_recipients
        return data

class MessageLogUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)
    
    class Meta:
        model = MessageLog
        fields = ['content']


class ResentLogMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_at']
            
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'name', 'content', 'created_at', 'updated_at']
        
class TemplateUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    
    class Meta:
        model = Template
        fields = ['name', 'content']