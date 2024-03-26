from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

project_description = '''
        ### Description
        ---
        This ***SMS Platform for Digital Marketers*** is a sophisticated web application\
        tailored to meet the specific requirements of digital marketers and businesses.\
        This platform offers a comprehensive suite of features designed to streamline\
        the process of sending SMS messages to multiple recipients. Leveraging the\
        capabilities of the Africa's Talking SMS API, users can efficiently create,\
        manage, and send personalized messages while benefiting from advanced\
        functionalities such as message templating, quick send options, and\
        detailed message history tracking. With its intuitive interface and\
        seamless integration with Africa's Talking API, the SMS Platform \
        or Digital Marketers provides users with a powerful tool to enhance\
        their communication strategies and engage with their target audience effectively.\n
        
        ---
        [Source Code](https://github.com/juliusmarkwei/sms-sender)
        
'''

schema_view = get_schema_view(
   openapi.Info(
      title="SwiftSend API Documentation - SMS Platform for Digital Marketers ®️",
      default_version='v1',
      description=project_description,
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="julius.markwei@stu.ucc.edu.gh"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)