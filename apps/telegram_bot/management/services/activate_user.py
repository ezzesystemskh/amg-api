from apps.auth_user.models import UserProfile
from apps.telegram_bot.management.services.activate_trigger_message import activate_message, inactivate_message

def activate_function(chat_id,data):
    user = UserProfile.objects.get(chat_id=chat_id)

    if data == "🔓 Activate":
        user.user_mode = "Activate"
        activate_message(chat_id)
    else:
        print("Inactivate is working.....")
        user.user_mode = "Inactivate"
        inactivate_message(chat_id)
    user.save()