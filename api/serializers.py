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

class ContactCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=True)
    info = serializers.CharField(required=False)
    created_by = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all(), required=True, write_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'info', 'created_by']



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
    

class RecipientLogDetailSerializer(serializers.ModelSerializer):
    contact_info = ContactDetailSerializer(source='contact_id', read_only=True)
    recipient_id = serializers.IntegerField(source='id')
    
    class Meta:
        model = RecipientLog
        fields = ['recipient_id', 'status', 'contact_info']
       
              
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
    contact_id = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), required=True)
    recipient_id = serializers.IntegerField(source='id')
    
    class Meta:
        model = RecipientLog
        fields = ['recipient_id', 'contact_id', 'status']


class MessageLogSerializer(serializers.ModelSerializer):
    recipients = RecipientLogSerializer(source='recipientlog_set', many=True, read_only=True)
    
    class Meta:
        model = MessageLog
        fields = ['id', 'content', 'sent_at', 'recipients']
        depth = 1
        
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
        fields = ['id', 'content', 'sent_at']
            
            
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ['id', 'name', 'content', 'created_at', 'updated_at']
        
        
class TemplateCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all(), required=True)
    class Meta:
        model = Template
        fields = ['id', 'name', 'content', 'created_at', 'updated_at', 'created_by']
        
        
class TemplateUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    
    class Meta:
        model = Template
        fields = ['name', 'content']