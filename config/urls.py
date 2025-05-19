from django.urls import path, include

urlpatterns = [
    path('telegram/', include('apps.telegram_bot.urls')),
    path('api/auth/', include('apps.auth_user.urls')),
]