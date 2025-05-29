import base64
from mimetypes import guess_type
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import uuid
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import QuerySet
from rest_framework import exceptions
from rest_framework.response import Response
from apps.auth_user.models import UserProfile
from apps.base.models import BaseImageFileModel
from apps.core.exceptions import BadRequestException
from apps.core.views import CoreCreateViewSet, CoreViewSet
from apps.emergency.constants import EMERGENCY_STEP
from apps.emergency.models import Emergency, EmergencyStep, EmergencyType
from apps.emergency.serializers import EmergencySerializer, EmergencyStepSerializer
import logging
from django.core.files.uploadedfile import SimpleUploadedFile

logger = logging.getLogger(__name__)


class EmergencyStepView(CoreViewSet):
    model = EmergencyStep
    queryset = EmergencyStep.objects.all()
    serializer_class = EmergencyStepSerializer


class EmergencyView(CoreCreateViewSet):
    model = Emergency
    queryset = Emergency.objects.all()
    serializer_class = EmergencySerializer
    

    def create(self, request, *args, **kwargs):
        chat_id = request.data.get("chat_id")
        emergency_type = request.data.get("emergency_type")
        longitude = request.data.get("longitude")
        latitude = request.data.get("latitude")
        files = request.FILES.get("files")
        file_path = request.data.get("files_path")
        text = request.data.get("text")
        voice = request.FILES.get("voice")
        voice_path = request.data.get("voice_path")
        is_completed = False
        is_checked = False

        if not files:
            # print("📸 No files received, trying to download from Telegram...")
            from apps.telegram_bot.views import TelegramWebhookView
            file_bytes = TelegramWebhookView.download_telegram_file(file_path)

            if file_bytes:
                ext = os.path.splitext(file_path)[1] or ".dat"
                content_type, _ = guess_type(file_path)
                if not content_type:
                    content_type = "application/octet-stream"

                file_name = f"telegram_file{ext}"

                files = SimpleUploadedFile(file_name, file_bytes, content_type=content_type)
                # print(f"✅ File received: {file_name} ({content_type})")
            else:
                # print("❌ Failed to download file bytes.")
                pass


        if not voice:
            print("📸 No files received, trying to download from Telegram...")
            from apps.telegram_bot.views import TelegramWebhookView
            voice_bytes = TelegramWebhookView.download_telegram_file(voice_path)

            if voice_bytes:
                ext = os.path.splitext(voice_path)[1] or ".dat"
                content_type, _ = guess_type(voice_path)
                if not content_type:
                    content_type = "application/octet-stream"

                file_name = f"telegram_file{ext}"

                voice = SimpleUploadedFile(file_name, voice_bytes, content_type=content_type)
                print(f"✅ File received: {file_name} ({content_type})")
            else:
                print("❌ Failed to download file bytes.")

        user_profile = self.get_user_profile(chat_id)
        emergency_type_instance = self.get_emergency_type_instance(emergency_type, user_profile)

        if not emergency_type:
            try:
                active_instance = self.get_active_emergency(chat_id, user_profile.first())
                emergency_step_type = active_instance.emergency_step.step_type
                emergency_type = active_instance.emergency_type.name
                on_step = self.get_next_step(active_instance)

                match emergency_step_type:
                    case EMERGENCY_STEP.LOCATION:
                        if None in (longitude, latitude):
                            return Response(
                                    {
                                        "message": "Wrong location",
                                        "error_code": "wrong_location"
                                    }
                                )

                        active_instance.longitude = longitude
                        active_instance.latitude = latitude
                        

                    case EMERGENCY_STEP.PHOTO_OR_VIDEO:
                        if not files:
                            return Response(
                                    {
                                        "message": "Wrong photo or video",
                                        "error_code": "wrong_photo_or_video"
                                    }
                                )

                        _, path = self.save_image(files, active_instance)

                        if path:
                            active_instance.image = path
                    
                    case EMERGENCY_STEP.TEXT_OR_VOICE:
                        print("=============================")
                        if not text and not voice:
                            return Response({
                                "message": "please send text",
                                "error": "wrong_text"
                            })
                        
                        if voice:
                            _, path = self.save_image(voice, active_instance)

                            if path:
                                active_instance.voice = path
                        active_instance.text = text
                        active_instance.is_completed = True
                    
                    case _:
                        raise exceptions.ValidationError({"error": "Invalid step type"})

                is_completed = active_instance.emergency_step.is_completed

                if not is_completed:
                    active_instance.emergency_step = on_step
                else:
                    is_checked = True
                    active_instance.is_checked = is_checked

                active_instance.save()

                instance = active_instance

            except Exception as error:
                logger.error(f"Error in emergency view: {error}")

                if isinstance(error, BadRequestException):
                    raise error

                self.update_previous_emergency_inactive(chat_id)
                return Response(
                    {
                        "message": "Not select Command",
                        "error_code": "wrong_step"
                    }
                )
        else:
            self.update_previous_emergency_inactive(chat_id)
            self.update_user_operation(emergency_type, user_profile)

            on_step = self.get_default_step(emergency_type_instance)
            instance = self.create_emergency_instance(
                request, on_step, user_profile.first()
            )
            is_completed = instance.is_completed

        if is_completed and is_checked:
            self.reset_user_operation(user_profile)
            user_profile.first().emergency_user_profile.filter(is_active=True).update(
                is_completed=True
            )
            return Response(self.get_serializer(instance).data)

        return Response(
            {
                "message": self.get_message(on_step, emergency_type),
            }
        )
    def reset_user_operation(self, user_profile):
        user_profile.update(operation=None)

    @staticmethod
    def generate_short_guid():
        uid = uuid.uuid4()
        short_uid = base64.urlsafe_b64encode(uid.bytes).rstrip(b'=').decode('utf-8')
        return short_uid

    def create_emergency_instance(self, request, on_step, user_profile):
        data = {
            "transaction_id": self.generate_short_guid(),
            "chat_id": request.data["chat_id"],
            "emergency_type": on_step.emergency_type.pk,
            "user_profile": user_profile.pk,
            "emergency_step": on_step.pk,
            "is_completed": on_step.is_completed,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer.instance

    def reset_user_operation(self, user_profile):
        user_profile.update(operation=None)

    def update_user_operation(self, emergency_type, user_profile: QuerySet):
        user_profile.update(operation=emergency_type)
    
    def get_default_step(self, emergency_type_instance):
        step = EmergencyStep.objects.filter(
            is_default=True, emergency_type=emergency_type_instance
        ).first()
        if not step:
            return Response({"error": "Default step not found"}, status=404)
        return step

    def update_previous_emergency_inactive(self, chat_id):
        Emergency.objects.filter(chat_id=chat_id).update(is_active=False)


    def get_user_profile(self, chat_id):
        user_profile = UserProfile.objects.filter(chat_id=chat_id)
        if not user_profile.exists():
            raise exceptions.ValidationError(
                {"error": "An error occurred, please press '/'start again"}
            )
        return user_profile
    
    def get_emergency_type_instance(self,emergency_type, user_profile):
        emergency_type_instance = EmergencyType.objects.filter(name=emergency_type).first()
        if (
            not emergency_type
            and user_profile.first()
            .emergency_user_profile.all()
            .filter(is_completed=True, is_active=True, is_checked=True)
            .exists()
        ):
            return Response({"error": "invalid_emergency_type"})
        elif emergency_type and not emergency_type_instance:
            return Response({"error": "Invalid_emergency_type"})

        return emergency_type_instance
    

    def get_active_emergency(self, chat_id, user_profile_instance):
        instance = Emergency.objects.filter(
            chat_id=chat_id,
            emergency_type__name=user_profile_instance.operation,
            user_profile=user_profile_instance.pk,
            is_active=True,
        ).first()

        return instance
    
    def get_next_step(self, active_instance):
        next_step = active_instance.emergency_step.step_num + 1
        on_step = EmergencyStep.objects.filter(
            step_num=next_step, emergency_type=active_instance.emergency_type
        ).first()
        return on_step
    

    def save_image(self, files, active_instance):
        custom_path = f"storages/{active_instance.emergency_type.name}/{files.name}"
        saved_path = default_storage.save(custom_path, ContentFile(files.read()))

        content_type = ContentType.objects.get_for_model(Emergency)

        image_file_instance = BaseImageFileModel(
            file_url=saved_path,
            content_type=content_type,
            object_id=active_instance.pk,
        )
        image_file_instance.save()
        return image_file_instance, saved_path
    
    def get_message(self, step_name, emergency_type):
        # TODO: Custom messages
        return f"{step_name.name}"