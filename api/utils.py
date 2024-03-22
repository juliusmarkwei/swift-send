from messages_logs.models import MessageLog, RecipientLog
from contacts.models import Contact


def clean_contacts(contacts):
    contact_lists = []
    
    if ',' in contacts:
        contact_lists = [recipient.strip() for recipient in contacts.split(',')]
    elif ' ' in contacts:
        contact_lists = [recipient.strip() for recipient in contacts.split()]
    elif ';' in contacts:
        contact_lists = [recipient.strip() for recipient in contacts.split(';')]
    elif '\n' in contacts:
        contact_lists = [recipient.strip() for recipient in contacts.split('\n')]
    else:
        contact_lists.append(contacts.strip())
        
    return contact_lists


def save_new_contact(phone_number, user):
    return Contact.objects.create(phone=phone_number, created_by=user)

def create_message_logs(message: str, user, recipient_lists: list, status: str):
    message_log = MessageLog.objects.create(content=message, author=user, status=status)
    
    for recipient in recipient_lists:
        try:
            contact = Contact.objects.get(phone=recipient, created_by=user)
            RecipientLog.objects.create(contact=contact, message=message_log)
        except Contact.DoesNotExist:
            saved_contact = save_new_contact(recipient, user)
            RecipientLog.objects.create(contact=saved_contact, message=message_log)