from django.http import HttpRequest
from apps.emergency.views import EmergencyView
from apps.telegram_bot.management.services.activate_trigger_message import activate_message, inactivate_message
from apps.telegram_bot.management.services.check_user_mode import user_mode
from lang.lang_config import translate


def handle_voice_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    voice = message.get("voice")
    if not voice:
        return

    file_id = voice["file_id"]

    from apps.telegram_bot.views import TelegramWebhookView
    voice_path = TelegramWebhookView.get_file_path(file_id)
    if not voice_path:
        return

    data = {
        "chat_id": chat_id,
        "voice_path": voice_path
    }

    fake_request = HttpRequest()
    fake_request.data = data

    view = EmergencyView()
    view.request = fake_request
    view.action = "create"
    view.format_kwarg = {}

    response = view.create(fake_request)
    response_data = response.data
    message = response_data.get('message')
    is_completed = response_data.get("is_completed", "")
    user = user_mode(chat_id)

    try:
        if is_completed == True:
            TelegramWebhookView.send_message(chat_id, text=translate("success_submit", chat_id))
            if user == "Activate":
                activate_message(chat_id)
            elif user == "Inactivate":
                inactivate_message(chat_id)
            return
        
        elif message == "Not select Command":
            TelegramWebhookView.send_message(chat_id, text=translate("select_any_command_first", chat_id))
            return
        
        elif message == "Wrong location":
            TelegramWebhookView.send_message(chat_id, text=translate("send_location_first", chat_id))
            return
        
        elif message == "Wrong photo or video":
            TelegramWebhookView.send_message(chat_id, text=translate("send_image_or_video_first", chat_id))
            return
    
    except Exception as e:
        print("Error in Handle Voice:", e)
