from django.urls import path, include
from rest_framework import routers
from apps.auth_user.views import UserCreateViewSet, UserLookUpView

router = routers.SimpleRouter(trailing_slash=False)
router.register("user", UserLookUpView)


urlpatterns = [
    path("", include(router.urls)),
    path("register", UserCreateViewSet.as_view()),
]
