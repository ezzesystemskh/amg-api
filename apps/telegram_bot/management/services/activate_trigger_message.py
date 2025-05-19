from apps.telegram_bot.management.services.check_user_mode import user_mode
from lang.lang_config import translate


def activate_message(chat_id):
    from apps.telegram_bot.views import TelegramWebhookView
    check_user_mode = user_mode(chat_id)
    if check_user_mode == "Inactivate":
        activate_mode = "🔒 Inactivate"
        button_message = translate("Activate_message",chat_id)

    else:
        activate_mode = "🔓 Activate"
        button_message = translate("Inactivate_message",chat_id)
    
    buttons = [
        [
            {"text": activate_mode, "callback_data": activate_mode},
        ],
        [
            {"text": "🔥 Fire", "callback_data": "fire_help"},
            {"text": "🚑 Ambulance", "callback_data": "ambulance_help"},
            {"text": "👮 Police", "callback_data": "police_help"},
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