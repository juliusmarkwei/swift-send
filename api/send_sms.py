import africastalking
from decouple import config

username = config('USERNAME')
api_key = config('API_KEY')

africastalking.initialize(username, api_key)

sms = africastalking.SMS

# Or use it asynchronously
def on_finish(error, response):
    if error is not None:
        raise error
    print(response)
      
def send_sms(message: str, to: list):
    response = sms.send(message, to, callback=on_finish)
    # return response