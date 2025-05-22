from django.http import HttpRequest

from apps.emergency.views import EmergencyView
from lang.lang_config import translate


def handle_photo_message(update):
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        caption = message.get("caption", "")

        photos = message.get("photo", [])
        if not photos:
            return

        file_id = photos[-1]["file_id"]

        from apps.telegram_bot.views import TelegramWebhookView
        file_path = TelegramWebhookView.get_file_path(file_id)
        if not file_path:
            return

        data = {
            "chat_id": chat_id,
            "files_path": file_path,
        }
        
        fake_request = HttpRequest()
        fake_request.data = data
        view = EmergencyView()
        view.request = fake_request
        view.action = "create"
        view.format_kwarg = {}

        reponse = view.create(fake_request)
        response_data = reponse.data
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
            print("Error in Handle Photo:", e)