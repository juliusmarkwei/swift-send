from src.message_logs.models import MessageLog, RecipientLog
from src.contacts.models import Contact
from .send_sms import send_sms


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
    messageLogObject = MessageLog.objects.create(content=message, author=user)
    return messageLogObject
    
            
def create_recipient_log(recipient_lists: list, messageLogInstace, response: dict, user):
    for recipient_data in response.get("SMSMessageData", {}).get("Recipients", []):
        recipient_number = recipient_data.get("number")
        recipient_status = recipient_data.get("status")
        print(recipient_number, recipient_status)
        recipient_contact = Contact.objects.get(phone=recipient_number, created_by=user)
        
        recipient_log = RecipientLog.objects.create(message=messageLogInstace, contact=recipient_contact, status=recipient_status)
        recipient_log.save()
