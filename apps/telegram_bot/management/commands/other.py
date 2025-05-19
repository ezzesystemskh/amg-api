from lang.lang_config import translate

def other_command(chat_id):
    from apps.telegram_bot.views import TelegramWebhookView

    fire_message = translate('other_command', chat_id)
    escaped_fire = TelegramWebhookView.escape(fire_message)
    TelegramWebhookView.send_message(
    chat_id,
        text=f"*{escaped_fire}*",
        reply_markup=TelegramWebhookView.remove_reply_keyboard(),
        parse_mode="MarkdownV2"
    )