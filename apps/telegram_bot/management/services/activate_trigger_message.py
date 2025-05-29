from apps.telegram_bot.management.services.check_user_mode import user_mode
from lang.lang_config import translate


def activate_message(chat_id):
    from apps.telegram_bot.views import TelegramWebhookView
    activate_mode = "🔒 Inactivate"
    activate_mess = "🔒 Activate Practice Action"
    button_message = translate("Activate_message",chat_id)

    buttons = [
        [
            {"text": activate_mess, "callback_data": activate_mode},
        ],
        [
            {"text": "🔥 Fire", "callback_data": "fire_help"},
            {"text": "🚑 Ambulance", "callback_data": "ambulance_help"},
            {"text": "👮 Police", "callback_data": "police_help"},
        ],
        [
            {"text": "💧 Water", "callback_data": "water_help"},
            {"text": "⚡ EDC", "callback_data": "edc_help"},
            {"text": "🚧 Road", "callback_data": "road_help"},
        ],
        [
            {"text": "🆘 Other", "callback_data": "other_help"}
        ]
    ]

    button_mss = TelegramWebhookView.escape(button_message)
    TelegramWebhookView.send_inline_keyboard(
        chat_id=chat_id,
        text=f"*{button_mss}*",
        buttons=buttons,
        parse_mode="MarkdownV2"
)
    
def inactivate_message(chat_id):
    from apps.telegram_bot.views import TelegramWebhookView
    activate_mode = "🔓 Activate"
    activate_mess = "🔓 Activate Serious Action"
    button_message = translate("Inactivate_message",chat_id)
    
    buttons = [
        [
            {"text": activate_mess, "callback_data": activate_mode},
        ],
        [
            {"text": "🔥 Fire", "callback_data": "fire_help"},
            {"text": "🚑 Ambulance", "callback_data": "ambulance_help"},
            {"text": "👮 Police", "callback_data": "police_help"},
        ],
        [
            {"text": "💧 Water", "callback_data": "water_help"},
            {"text": "⚡ EDC", "callback_data": "edc_help"},
            {"text": "🚧 Road", "callback_data": "road_help"},
        ],
        [
            {"text": "🆘 Other", "callback_data": "other_help"}
        ]
    ]

    button_mss = TelegramWebhookView.escape(button_message)
    TelegramWebhookView.send_inline_keyboard(
        chat_id=chat_id,
        text=f"*{button_mss}*",
        buttons=buttons,
        parse_mode="MarkdownV2"
)