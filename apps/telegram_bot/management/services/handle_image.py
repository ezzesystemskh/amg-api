from django.http import HttpRequest

from apps.emergency.views import EmergencyView


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
        print("Message:", message)