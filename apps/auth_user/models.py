from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    Permission,
)
from apps.core.models import AbstractModel
from django.db import models

STATUS = (
    ("inactive", "Inactive"),
    ("active", "Active"),
    ("pending", "Pending"),
)


class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        user = self.create_user(username, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, AbstractModel):
    username = models.CharField(max_length=55, unique=True)
    chat_id = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_default_password = models.BooleanField(default=True)
    groups = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="user_groups",
        blank=True,
        null=True,
    )
    objects = UserManager()
    USERNAME_FIELD = "username"

    class Meta:
        db_table = "auth_user_user"

    def __str__(self):
        return self.username

    def user_permissions(self):
        if not self.groups:
            return Permission.objects.none()
        return self.groups.permissions.all()

    def has_perm(self, perm, obj=None):
        user_perms = self.user_permissions()
        return self.is_superuser or (
            user_perms and user_perms.filter(codename=perm).exists()
        )

    def has_module_perms(self, app_label):
        user_perms = self.user_permissions()
        return self.is_superuser or (
            user_perms and user_perms.filter(content_type__app_label=app_label).exists()
        )


class UserProfile(AbstractModel):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="user_profile",
        null=True,
        blank=True,
    )
    chat_id = models.CharField(max_length=255)
    first_name = models.CharField(max_length=55, null=True, blank=True)
    last_name = models.CharField(max_length=55, null=True, blank=True)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=55, choices=STATUS, default="active")
    language = models.CharField(max_length=55, null=True, blank=True, default="en")

    class Meta:
        db_table = "user_profile"
