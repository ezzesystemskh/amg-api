from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.core.models import AbstractModel


class BaseImageFileModel(AbstractModel):
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    file_url = models.ImageField(upload_to="storages/emergency")
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content_type.name + " " + str(self.object_id)