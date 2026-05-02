from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("docs.urls")),
    path('api/v1/auth/', include("users.urls")),
    path('api/v1/', include("expedition.urls"))
]
