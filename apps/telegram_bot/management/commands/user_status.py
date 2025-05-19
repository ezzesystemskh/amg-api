from apps.auth_user.models import User
from lang.lang_config import translate


def check_user_status(context):
    print("Check Command")
    from apps.telegram_bot.views import TelegramWebhookView
    user = User.objects.filter(chat_id=context.get("chat_id", '')).first()
    print("user:",user)
    user_status = user.user_profile.status
    user_def_pw = user.is_default_password
    return user_status, user_def_pw