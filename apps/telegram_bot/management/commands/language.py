from apps.auth_user.models import User
from apps.telegram_bot.management.commands.user_status import check_user_status
from lang.lang_config import translate


def handle_language_selection(context, language_text):
    from apps.telegram_bot.views import TelegramWebhookView

    print("Handle Language Command Is Working...")
    user = User.objects.filter(chat_id=context["chat_id"]).first()
    if language_text == "🇬🇧 English":
        user.user_profile.language = "en"
        user.user_profile.save()
        response = "You have selected English."

    else:
        user.user_profile.language = "kh"
        user.user_profile.save()
        response = "អ្នកបានជ្រើសរើសភាសាខ្មែរ"

    user_status, user_df_pw = check_user_status(context)
    user_status = "active"
    if user_status == "pending":
        TelegramWebhookView.send_message(
            context["chat_id"], response, reply_markup={"remove_keyboard": True}
        )
        TelegramWebhookView.send_message(
            context["chat_id"], translate("pending_user", context["chat_id"])
        )

    elif user_status == "inactive":
        TelegramWebhookView.send_message(
            context["chat_id"],
            translate("inactive_user", context["chat_id"]),
            reply_markup={"remove_keyboard": True},
        )
    elif user_status == "active":
        from django.core.cache import cache

        password = cache.get(f"temp_pw_{context['chat_id']}")
        TelegramWebhookView.send_message(
            context["chat_id"], response, reply_markup={"remove_keyboard": True}
        )
        # TelegramWebhookView.send_message(
        #         context["chat_id"],
        #         f"Your PIN:\n```\n{password}\n```",
        #         parse_mode="MarkdownV2"
        #     )
        from apps.telegram_bot.management.commands.amg import amg_command

        TelegramWebhookView.set_telegram_command(context)
        if not user_df_pw:
            return
        amg_command(context)


def language_command(context):
    from apps.telegram_bot.views import TelegramWebhookView

    buttons = [["🇬🇧 English", "🇰🇭 Khmer"]]

    user_status = check_user_status(context)
    user_status = "ok"
    if user_status == "inactive":
        TelegramWebhookView.send_message(
            context["chat_id"],
            translate("inactive_user", context["chat_id"]),
            reply_markup={"remove_keyboard": True},
        )
        return

    TelegramWebhookView.send_keyboard(
        chat_id=context["chat_id"],
        text=translate("choose_language", context.get("chat_id")),
        buttons=buttons,
    )
