from django.urls import path, include
from rest_framework import routers
from apps.emergency.views import EmergencyView, EmergencyStepView

router = routers.DefaultRouter(trailing_slash=True)
router.register(r"emergency_step", EmergencyStepView)

urlpatterns = [
    path("", include(router.urls)),
    path("emergency", EmergencyView.as_view()),
]
