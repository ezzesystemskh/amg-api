from django.http import HttpRequest
from apps.emergency.views import EmergencyView
from lang.lang_config import translate

def handle_location_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    location = message.get("location", {})
    from apps.telegram_bot.views import TelegramWebhookView

    if not location:
        TelegramWebhookView.send_message(chat_id,text=translate("not_live_location", chat_id))

    lat = location.get("latitude", "")
    lon = location.get("longitude", "")

    data = {
        "chat_id": chat_id,
        "latitude": lat,
        "longitude": lon,
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

        print("message: ",message)
        if message == "Please send your photo":
            TelegramWebhookView.send_message(chat_id,text=translate("send_your_photo", chat_id))
            return
        
        elif message == "Not select Command":
            TelegramWebhookView.send_message(chat_id, text=translate("select_any_command_first", chat_id))
            return
        
        elif message == "Wrong photo or video":
            TelegramWebhookView.send_message(chat_id, text=translate("send_image_or_video_first", chat_id))
            return           
            
    except Exception as e:
        print("Error in Location:",e)