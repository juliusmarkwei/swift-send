from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

project_description = '''
    The SMS Distribution System is a web application designed to streamline the process of creating,\
        managing, and distributing SMS messages to contacts. The system allows users to create message\
            templates, manage contacts, associate contacts with templates, and send SMS messages to selected\
                contacts. It features user authentication and authorization to ensure secure access to the system
'''

schema_view = get_schema_view(
   openapi.Info(
      title="SMS Sender Application",
      default_version='v1',
      description=project_description,
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="julius.markwei@stu.ucc.edu.gh"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)