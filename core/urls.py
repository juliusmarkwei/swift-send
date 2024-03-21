from django.contrib import admin
from django.urls import path, include
from api.utils import schema_view
from djoser import urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('api/', include('api.urls')),
    path('', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
