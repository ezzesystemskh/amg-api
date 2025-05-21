from django.http import HttpRequest
from apps.emergency.views import EmergencyView
from lang.lang_config import translate

def ambulance_command(chat_id):
    from apps.telegram_bot.views import TelegramWebhookView
    
    data = {
        "chat_id": chat_id,
        "emergency_type": "ambulance"
    }
    fire_message = translate('ambulance_command', chat_id)
    escaped_fire = TelegramWebhookView.escape(fire_message)

    fake_request = HttpRequest()
    fake_request.data = data
    view = EmergencyView()
    view.request = "create"
    view.format_kwarg = {}

    response = view.create(fake_request)
    response_data = response.data
    message = response_data.get('message')

    if message == "Please send your location":
        TelegramWebhookView.send_message(
        chat_id,
            text=f"*{escaped_fire}*",
            reply_markup=TelegramWebhookView.remove_reply_keyboard(),
            parse_mode="MarkdownV2"
        )
        return
    
    TelegramWebhookView.send_message(chat_id,text=translate("ambulance_not_work_message", chat_id))
