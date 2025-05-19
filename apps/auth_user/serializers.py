from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers
from apps.auth_user.models import User, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"

class UserSerializer(WritableNestedModelSerializer):
    user_profile = UserProfileSerializer()

    class Meta:
        model = User
        exclude = ["is_staff", "is_superuser", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def to_internal_value(self, data):  
        data["user_profile"]["chat_id"] = data.get("chat_id")
        return super().to_internal_value(data)