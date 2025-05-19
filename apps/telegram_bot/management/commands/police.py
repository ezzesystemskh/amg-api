from lang.lang_config import translate

def police_command(context):
    from apps.telegram_bot.views import TelegramWebhookView

    TelegramWebhookView.send_message(
        context.get("chat_id"),
        text=f"{translate('help_command', context.get('chat_id', ''))}",
        reply_markup=TelegramWebhookView.remove_reply_keyboard(),
    )
