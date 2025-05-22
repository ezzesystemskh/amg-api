from django.http import HttpRequest
from apps.emergency.views import EmergencyView
from apps.telegram_bot.management.services.activate_trigger_message import activate_message, inactivate_message
from apps.telegram_bot.management.services.check_user_mode import user_mode
from lang.lang_config import translate


def handle_text_message(context, text):
    chat_id = context.get('chat_id', '')
    from apps.telegram_bot.views import TelegramWebhookView
    data = {
        "chat_id": chat_id,
        "text": text
    }

    fake_request = HttpRequest()
    fake_request.data = data
    view = EmergencyView()
    view.request = fake_request
    view.action = "create"
    view.format_kwarg = {}

    response = view.create(fake_request)

    try:
        response_data = response.data
        message = response_data.get("message", "")
        is_completed = response_data.get("is_completed", "")
        print("message:", message)
        user = user_mode(chat_id)
        
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
        print("This is error in handle text: ", e)
