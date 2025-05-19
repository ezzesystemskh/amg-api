from apps.auth_user.models import User
from apps.auth_user.views import UserCreateViewSet
from django.http import HttpRequest
from apps.telegram_bot.management.commands.amg import amg_command
from apps.telegram_bot.management.commands.user_status import check_user_status
from lang.lang_config import translate
from apps.telegram_bot.management.commands.language import language_command


def start_command(context):
    print("Start Command is Working...")
    from apps.telegram_bot.views import TelegramWebhookView

    if not User.objects.filter(username=context.get("username")).exists():
        data = {
            "username": context.get("username", ""),
            "chat_id": context.get("chat_id", ""),
            "user_profile": {
                "first_name": context.get("first_name", ""),
                "last_name": context.get("last_name", ""),
            },
        }

        # Create a mock request
        fake_request = HttpRequest()
        fake_request.data = data
        view = UserCreateViewSet()
        view.request = fake_request
        view.action = "create"
        view.format_kwarg = {}

        response = view.create(fake_request)
        response_data = response.data
        password = response_data.get("password")
        from django.core.cache import cache

        cache.set(f"temp_pw_{context['chat_id']}", password, timeout=3000)

        TelegramWebhookView.send_message(
            context.get("chat_id"),
            translate("new_user_start_message", context.get("chat_id")),
        )

        language_command(context)
        return

    fullname = context.get("first_name", "") + " " + context.get("last_name", "")
    welcome = translate("welcome_old_user", context.get("chat_id"))
    greeting = translate("greeting_old_user", context.get("chat_id"))

    user_status = check_user_status(context)
    user_status = "OK"
    if user_status == "pending":
        TelegramWebhookView.send_message(
            context.get("chat_id"),
            translate("pending_user", context.get("chat_id")),
        )
        return

    elif user_status == "inactive":
        TelegramWebhookView.send_message(
            context.get("chat_id"),
            translate("inactive_user", context.get("chat_id")),
        )
        return

    TelegramWebhookView.set_telegram_command(context)
    # TelegramWebhookView.send_message(
    #     context.get("chat_id"), f"{welcome} {fullname} {greeting}"
    # )
    amg_command(context)

