from accounts.models import UserAccount
from contacts.models import Contact
from messages_center.models import Message
from msg_templates.models import Template
from rest_framework import serializers
from django.contrib.auth.hashers import make_password



class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        
        # Adding the below line made it work for me.
        instance.is_active = True
        if password is not None:
            # Set password does the hash, so you don't need to call make_password 
            instance.set_password(password)
        instance.save()
        return instance
    

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'info', 'created_by', 'created_at', 'updated_at']
        
        
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'message_content', 'created_by', 'status', 'created_at', 'updated_at']
        
        
class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'