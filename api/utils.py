from src.message_logs.models import MessageLog, RecipientLog
from src.contacts.models import Contact
from .send_sms import send_sms
from rest_framework.response import Response
from rest_framework import status


def clean_contacts(contacts):
    if isinstance(contacts, list):
        return [contact.strip() for contact in contacts]

    contact_lists = []
    delimiters = [',', ';', ' ', '\n']

    for delimiter in delimiters:
        if delimiter in contacts:
            contact_lists = [recipient.strip() for recipient in contacts.split(delimiter)]
            break
    if not contact_lists:
        contact_lists.append(contacts.strip())
        
    return contact_lists



def save_new_contact(phone_number, user):
    return Contact.objects.create(phone=phone_number, created_by=user)

def create_message_logs(message: str, user):
    messageLogObject = MessageLog.objects.create(content=message, author_id=user)
    return messageLogObject
    
            
def create_recipient_log(recipient_lists: list, messageLogInstace, response: dict, user):
    for recipient_data in response.get("SMSMessageData", {}).get("Recipients", []):
        recipient_number = recipient_data.get("number")
        if recipient_number:
            recipient_status = recipient_data.get("status")
            
            # Query the Contact object only if recipient_number is not None
            recipient_contact = Contact.objects.filter(phone=recipient_number, created_by=user).first()
            if recipient_contact:
                recipient_log = RecipientLog.objects.create(message_id=messageLogInstace, contact_id=recipient_contact, status=recipient_status)
                recipient_log.save()
            else:
                # Handle case where no Contact object is found for the recipient_number
                print(f"No Contact found for recipient number: {recipient_number}")
        else:
            # Handle case where recipients_number is None
            return Response({"message": "Recipient number is deleted from your contact!"}, status=status.HTTP_400_BAD_REQUEST)
