import africastalking
from decouple import config

africastalking.initialize(
    username=config('AFRICASTALKING_USERNAME'),
    api_key=config('AFRICASTALKING_API_KEY')
)


sms = africastalking.SMS
def send_sms(message: str, to: list, sender: str=None):
    try:
        return sms.send(message, to, sender)
    except Exception as e:
        print (f'Hey, we have a problem: {e}')
