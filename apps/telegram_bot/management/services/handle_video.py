

from django.http import HttpRequest

from apps.emergency.views import EmergencyView
from lang.lang_config import translate


def handle_video_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    caption = message.get("caption", "")

    from apps.telegram_bot.views import TelegramWebhookView

    file_id = None

    if "video" in message:
        video = message.get("video", {})
        file_id = video.get("file_id")

    if not file_id:
        return

    file_path = TelegramWebhookView.get_file_path(file_id)
    if not file_path:
        return

    data = {
        "chat_id": chat_id,
        "files_path": file_path
    }

    fake_request = HttpRequest()
    fake_request.data = data
    view = EmergencyView()
    view.request = fake_request
    view.action = "create"
    view.format_kwarg = {}

    try:
        response = view.create(fake_request)
        response_data = response.data
        message = response_data.get('message')

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
        print("Error in Handle Media (Photo/Video):", e)