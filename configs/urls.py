from django.contrib import admin
from django.urls import include, path

from app.views import upload

urlpatterns = [
    path('', include('app.urls')),
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),
]
