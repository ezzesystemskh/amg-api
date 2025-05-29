import base64
import uuid
from django.db import models
from apps.core.models import AbstractModel
from apps.auth_user.models import UserProfile


EMERGENCY_TYPE = (
    ("police", "POLICE"),
    ("ambulance", "AMBULANCE"),
    ("fire", "FIRE"),
)

EMERGENCY_STEP = (
    ("location", "Location"),
    ("photo_or_video", "Photo_OR_Video"),
    ("text_or_voice", "Text_Or_Voice"),
)

class EmergencyType(AbstractModel):
    name = models.CharField(
        choices=EMERGENCY_TYPE,
        max_length=55,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "emergency_type"


class EmergencyStep(AbstractModel):
    step_num = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    step_type = models.CharField(
        choices=EMERGENCY_STEP,
        max_length=55,
    )
    emergency_type = models.ForeignKey(
        EmergencyType,
        on_delete=models.DO_NOTHING,
        related_name="emergency_type_step",
        null=True,
        blank=True,
    )
    expect = models.CharField(max_length=55, null=True, blank=True)


    class Meta:
        db_table = "emergency_step"


class Emergency(AbstractModel):
    date = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=55, blank=True, null=True)
    latitude = models.CharField(max_length=55, blank=True, null=True)
    emergency_type = models.ForeignKey(
        EmergencyType,
        on_delete=models.DO_NOTHING,
        related_name="emergency_type_emergency",
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to="emergency/", blank=True, null=True)
    voice = models.FileField(upload_to="emergency/", blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    emergency_step = models.ForeignKey(
        EmergencyStep,
        on_delete=models.DO_NOTHING,
        related_name="emergency_step",
        null=True,
        blank=True
    )
    chat_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.DO_NOTHING,
        related_name="emergency_user_profile",
        null=True,
        blank=True,
    )
    is_checked = models.BooleanField(default=False)
    
    class Meta:
        db_table = "emergency"