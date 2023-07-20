import os

from django.conf import settings
from django.db import models


class FileUpload(models.Model):
    file = models.FileField()
    path = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self):
        super().save()
        self.path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        super().save()
