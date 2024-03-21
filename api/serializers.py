from accounts.models import UserAccount
from contacts.models import Contact
from messages_logs.models import MessageLog, ReceipientLog
from msg_templates.models import Template
from rest_framework import serializers
from django.contrib.auth.hashers import make_password



class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'created_at', 'updated_at']
        
  

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'info', 'created_by', 'created_at', 'updated_at']
        
        
class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_by', 'status', 'sent_at']

class ReceipientLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceipientLog
        fields = ['id', 'contact', 'message']

        
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'
        