from apps.telegram_bot.management.services.check_user_mode import user_mode
from lang.lang_config import translate


def amg_command(context):
    from apps.telegram_bot.views import TelegramWebhookView
    amg_message = translate('amg_command', context.get('chat_id', ''))
    amg_escaped = TelegramWebhookView.escape(amg_message)
    check_user_mode = user_mode(context.get('chat_id', ''))
    if check_user_mode == "Inactivate":
        activate_mode = "🔓 Activate"
        button_message = translate("inactive_buttons_message",context.get('chat_id', ''))

    else:
        activate_mode = "🔒 Inactivate"
        button_message = translate("active_buttons_message",context.get('chat_id', ''))

    TelegramWebhookView.send_message(
                context["chat_id"],
                f"*{amg_escaped}*",
                parse_mode="MarkdownV2"
        )
    
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
        chat_id=context["chat_id"],
        text=f"*{button_mss}*",
        buttons=buttons,
        parse_mode="MarkdownV2"
)
    

