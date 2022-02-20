
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Household API",
      default_version='v1',
      description="API for Household app",
      terms_of_service="https://www.xzit.com.au/",
      contact=openapi.Contact(email="xzitit@gmail.com"),
      license=openapi.License(name="XZIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.api.urls'), name='account-api'),
    path('api/calculation/', include('calculation.api.urls'), name='calculation-api'),
    path('api/group/', include('group.api.urls'), name='group-api'),
    # path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('apiview/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('apidoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


]
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
