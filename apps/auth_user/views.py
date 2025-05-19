from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from apps.auth_user.models import User, UserProfile
from apps.auth_user.serializers import UserSerializer, UserProfileSerializer
from apps.core.views import CoreViewSet, CoreCreateViewSet, CoreListViewSet
from apps.core.exceptions import BadRequestException
from django.db import transaction
import random
from rest_framework.permissions import IsAuthenticated


class UserCreateViewSet(CoreCreateViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = request.data

        data = {
            **data,
            "is_staff":False,
            "is_superuser": False,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        instance = serializer.instance

        generated_password = str(random.randint(100000, 999999))

        print("Generated Password:", generated_password)

        instance.set_password(generated_password)
        instance.save()

        response = {
            **serializer.data,
            "password": generated_password
        }

        return Response(response, status=status.HTTP_201_CREATED)


class UserLookUpView(CoreViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]