import africastalking
from decouple import config
from rest_framework.response import Response
from rest_framework import status

africastalking.initialize(
    username=config('AFRICASTALKING_USERNAME'),
    api_key=config('AFRICASTALKING_API_KEY')
)


sms = africastalking.SMS
def send_sms(message: str, to: list, sender: str=None):
    try:
        return sms.send(message, to, sender)
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})

