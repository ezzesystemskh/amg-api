import json
import re
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views import View
import requests
from apps.telegram_bot.management.commands.ambulance import ambulance_command
from apps.telegram_bot.management.commands.fire import fire_command
from apps.telegram_bot.management.commands.help import help_command
from apps.telegram_bot.management.commands.amg import amg_command
from apps.telegram_bot.management.commands.language import (
    handle_language_selection,
    language_command,
)
from apps.telegram_bot.management.commands.other import other_command
from apps.telegram_bot.management.commands.police import police_command
from apps.telegram_bot.management.commands.share_contact import (
    handle_share_contact,
    share_contact_command,
)
from apps.telegram_bot.management.commands.start import start_command
from telegram.helpers import escape_markdown

from apps.telegram_bot.management.services.activate_user import activate_function


class TelegramWebhookView(View):
    def post(self, request, *args, **kwargs):
        update = json.loads(request.body.decode("utf-8"))
        self.handle_update(update)
        return HttpResponse("OK")

    def get_user_profile(self, user_id):
        
        photo_url = None
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUserProfilePhotos",
                params={"user_id": user_id}
            ).json()
            
            if response.get('ok') and response['result']['total_count'] > 0:
                file_id = response['result']['photos'][0][-1]['file_id']
                
                file_response = requests.get(
                    f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getFile",
                    params={"file_id": file_id}
                ).json()
                
                if file_response.get('ok'):
                    file_path = file_response['result']['file_path']
                    photo_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{file_path}"

                return photo_url
        
        except Exception as e:
            print(f"Error getting profile photo: {e}")
            photo_url = None

    def handle_update(self, update):
        if "message" in update:
            self.handle_message(update["message"])
        elif "callback_query" in update:
            self.handle_callback_query(update["callback_query"])

    def handle_callback_query(self, callback_query):
        chat_id = callback_query["message"]["chat"]["id"]
        data = callback_query["data"]

        print("User clicked:", data)

        if data == "🔓 Activate":
            activate_function(chat_id,data)

        elif data == "🔒 Inactivate":
            activate_function(chat_id,data)

        elif data == "fire_help":
            fire_command(chat_id)
        
        elif data == "police_help":
            police_command(chat_id)

        elif data == "ambulance_help":
            ambulance_command(chat_id)

        elif data == "other_help":
            other_command(chat_id)

        else:
            self.send_message(chat_id, f"Wrong Buttons")

    def handle_message(self, message):
        user = message.get("from", {})
        text = message.get("text", "")
        user_id = user.get('id')
        user_profile = self.get_user_profile(user_id)
        print("Last Name From Handle:",user.get("last_name", ""))
        context = {
            "user_id": user.get('id'),
            "chat_id": message["chat"]["id"],
            "username": user.get("username", ""),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "fullname": f"{user.get('first_name', '')} {user.get('last_name', '')}",
            "photo_url": user_profile
        }


        # Handle commands
        if text.startswith("/"):
            command = text.split()[0]
            self.handle_command(context, command)

        elif text in ["🇬🇧 English", "🇰🇭 Khmer"]:
            handle_language_selection(context, text)

        elif "contact" in message:
            contact = message["contact"]
            handle_share_contact(context, contact)
        
    def handle_command(self, context, command):
        print("This is command:",command)
        if command == "/start":
            start_command(context)

        elif command == "/language":
            language_command(context)

        elif command == "/share_contact":
            share_contact_command(context)

        elif command == "/help":
            help_command(context)

        elif command == "/Police":
            police_command(context)

        elif command == "/Ambulance":
            ambulance_command(context)

        elif command == "/Fire":
            fire_command(context)
        
        elif command == "/emg":
            amg_command(context)

        else:
            self.send_message(context.get("chat_id"), f"Unknown command: {command}")

    @classmethod
    def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        import requests

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        
        if parse_mode:
            payload["parse_mode"] = parse_mode

        if reply_markup:
            payload["reply_markup"] = reply_markup

        requests.post(url, json=payload)


    @staticmethod
    def set_telegram_command(context):
        from lang.lang_config import translate
        print(context["chat_id"])

        commands = [
            {"command": "Fire", "description": translate("fire_command", context["chat_id"])},
            {"command": "Ambulance", "description": translate("ambulance_command", context["chat_id"])},
            {"command": "police", "description": translate("police_command", context["chat_id"])},
            {"command": "language", "description": translate("language_command", context["chat_id"])},
            {"command": "share_contact", "description": translate("share_contact_command", context["chat_id"])},
            {"command": "help", "description": translate("help_command", context["chat_id"])},
            {"command": "start", "description": translate("start_command", context["chat_id"])},
        ]

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setMyCommands"

        data = {
            "commands": commands,
            "scope": {
                "type": "chat",
                "chat_id": int(context["chat_id"]) 
            }
        }
    
        response = requests.post(url, json=data)
        return response.json().get("ok", False)
    

    @staticmethod
    def create_keyboard(buttons, resize=True, one_time=True):
        """Creates a custom keyboard markup"""
        return {
            "keyboard": buttons,
            "resize_keyboard": resize,
            "one_time_keyboard": one_time,
        }

    @staticmethod
    def remove_reply_keyboard():
        return {"remove_keyboard": True}

    @staticmethod
    def send_keyboard(chat_id, text, buttons):
        """Sends message with keyboard"""
        keyboard = TelegramWebhookView.create_keyboard(buttons)
        payload = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}
        # Implement your actual message sending logic here
        return requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
        )

    @staticmethod
    def create_contact_button(text, request_contact=True):
        return {"text": text, "request_contact": request_contact}
    

    @staticmethod
    def escape(text):
        return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    @staticmethod
    def send_contact_request(chat_id, text, button_text):
        """
        Sends a message with a contact sharing button
        :param chat_id: Target chat ID
        :param text: Message text
        :param button_text: Text for the contact button
        """
        contact_button = TelegramWebhookView.create_contact_button(button_text)
        keyboard = {
            "keyboard": [[contact_button]],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }

        payload = {"chat_id": chat_id, "text": text, "reply_markup": keyboard}

        requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload,
        )

    @staticmethod
    def create_inline_keyboard(buttons):
        return {
            "inline_keyboard": buttons
        }
    
    @staticmethod
    def send_inline_keyboard(chat_id, text, buttons, parse_mode=None):

        keyboard = TelegramWebhookView.create_inline_keyboard(buttons)
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": keyboard
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode

        return requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json=payload
        )

    # @staticmethod
    # def create_mini_app_button(context):
    #     topup_url = f"""{settings.MINI_APP_URL}/?version=v2.1&telegram_id={context["chat_id"]}&full_name={context["fullname"]}&telegram_username={context["username"]}&photo_url={context["photo_url"]}"""
    #     print(topup_url)
    #     keyboard = {
    #         "inline_keyboard": [
    #             [
    #                 {
    #                     "text": "NEXT",
    #                     "web_app": {
    #                         "url": topup_url
    #                     }
    #                 }
    #             ]
    #         ]
    #     }
        
    #     return keyboard
    


telegram_webhook = csrf_exempt(TelegramWebhookView.as_view())
