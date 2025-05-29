from apps.telegram_bot.management.services.check_user_mode import user_mode
from lang.lang_config import translate


def amg_command(context):
    from apps.telegram_bot.views import TelegramWebhookView
    amg_message = translate('amg_command', context.get('chat_id', ''))
    amg_escaped = TelegramWebhookView.escape(amg_message)
    check_user_mode = user_mode(context.get('chat_id', ''))

    if check_user_mode == "Inactivate":
        activate_mode = "🔓 Activate"
        activate_mess = "🔓 Activate Serious Action"

    else:
        activate_mode = "🔒 Inactivate"
        activate_mess = "🔒 Activate Practice Action"
    
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

    TelegramWebhookView.send_inline_keyboard(
        chat_id=context["chat_id"],
        text=f"*{amg_escaped}*",
        buttons=buttons,
        parse_mode="MarkdownV2"
)
    

