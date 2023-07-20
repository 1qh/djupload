from django.urls import path

from .views import edit, select, upload

urlpatterns = [
    path('', upload, name='upload'),
    path('edit', edit, name='edit'),
    path('select', select, name='select'),
]
