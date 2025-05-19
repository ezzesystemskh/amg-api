import base64
import uuid
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from rest_framework import exceptions
from rest_framework.response import Response
from apps.auth_user.models import UserProfile
