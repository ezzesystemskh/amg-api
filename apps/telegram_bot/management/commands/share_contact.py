from apps.telegram_bot.management.commands.user_status import check_user_status
from lang.lang_config import translate
from apps.telegram_bot.management.commands.user_status import check_user_status


def share_contact_command(context):
    from apps.telegram_bot.views import TelegramWebhookView

    chat_id = context.get("chat_id", "")
    text = "Please Share Your Contact"
    button_text = "Share Contact"
    user_status = check_user_status(context)
    user_status = "OK"
    if user_status == "pending":
        TelegramWebhookView.send_message(
            context.get("chat_id"),
            translate("pending_user", context.get("chat_id")),
        )
        return

    elif user_status == "inactive":
        TelegramWebhookView.send_message(
            context.get("chat_id"),
            translate("inactive_user", context.get("chat_id")),
        )
        return

    TelegramWebhookView.send_contact_request(chat_id, text, button_text)


def handle_share_contact(context, contact):
    from apps.telegram_bot.views import TelegramWebhookView

    chat_id = context.get("chat_id", "")
    username = context.get("username", "")
    phone_number = contact.get("phone_number", "")
    first_name = context.get("first_name", "")
    last_name = context.get("last_name", "")
    fullname = first_name + " " + last_name

    text = f"""
Thanks for sharing your contact!
Fullname: {fullname}
Phone Number: {phone_number}
Username: https://t.me/{username}
"""
    TelegramWebhookView.send_message(
        chat_id, text, reply_markup=TelegramWebhookView.remove_reply_keyboard()
    )
