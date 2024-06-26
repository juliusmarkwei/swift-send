from src.accounts.models import UserAccount
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog
from src.msg_templates.models import Template
from rest_framework import serializers
from django.contrib.auth.hashers import make_password



class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'full_name', 'phone', 'created_at', 'updated_at']
        
  
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'phone', 'info']


class ContactCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=True)
    info = serializers.CharField(required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all(), required=True, write_only=True)
    
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'phone', 'info', 'created_by']


class ContactUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    info = serializers.CharField(required=False)
    
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'phone', 'info']


# MEssage log serializer and its related serializers
class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'phone', 'info']
    

# serializer for creating a new message log
class RecipientLogDetailSerializer(serializers.ModelSerializer):
    contact_info = ContactDetailSerializer(source='contact_id', read_only=True)
    
    class Meta:
        model = RecipientLog
        fields = ['status', 'contact_info']
       
class MessageLogDetailSerializer(serializers.ModelSerializer):
    recipients = RecipientLogDetailSerializer(source='recipientlog_set', many=True, read_only=True)
    
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_at', 'recipients']
        depth = 1

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data



class RecipientLogSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipientLog
        fields = ['contact', 'status']
    
    def get_contact(self, obj):
        return str(obj.contact_id)


class MessageLogSerializer(serializers.ModelSerializer):
    recipients = RecipientLogSerializer(source='recipientlog_set', many=True, read_only=True)
    
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_at', 'recipients']
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data
    

class MessageLogUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)
    
    class Meta:
        model = MessageLog
        fields = ['content']


class ResentLogMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['content', 'sent_at']
            

# Template serializer and its related serializers  
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['name', 'content', 'created_at', 'updated_at']
        
        
class TemplateCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all(), required=True, write_only=True)
    class Meta:
        model = Template
        fields = ['name', 'content', 'created_at', 'updated_at', 'created_by']
        
        
class TemplateUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    
    class Meta:
        model = Template
        fields = ['name', 'content']
    

# Serializers for Swagger ui documentation purposes
class ResendEditedMessageLogSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    
    
class SendMessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    contacts = serializers.ListField(required=True)
    

class ContactBodySerializer(serializers.Serializer):
    contacts = serializers.ListField(required=True)
    

class TemplateBodySerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    content = serializers.CharField(required=True)