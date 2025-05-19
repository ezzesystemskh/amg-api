from rest_framework import serializers
from apps.base.models import BaseImageFileModel


class BaseImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseImageFileModel
        fields = "__all__"