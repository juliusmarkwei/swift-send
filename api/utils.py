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
