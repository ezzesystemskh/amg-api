from django.http import HttpRequest
from apps.emergency.views import EmergencyView
from lang.lang_config import translate


def handle_voice_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    caption = message.get("caption", "")

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
        "voice_path": voice_path,
        "caption": caption,
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

    try:
        if message == "Please send your text":
            TelegramWebhookView.send_message(chat_id, text=translate("send_your_text", chat_id))
            return
        elif message == "Not select Command":
            TelegramWebhookView.send_message(chat_id, text=translate("select_any_command_first", chat_id))
            return
        elif message == "Wrong location":
            TelegramWebhookView.send_message(chat_id, text=translate("send_location_first", chat_id))
            return
    except Exception as e:
        print("Error in Handle Voice:", e)
