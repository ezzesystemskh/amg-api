from django.core.management.base import BaseCommand
from django.conf import settings
import requests


class Command(BaseCommand):
    help = "Set Telegram webhook"

    def handle(self, *args, **options):
        api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook?url={settings.WEBHOOK}"
        response = requests.get(api_url)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("Webhook set successfully"))
        else:
            self.stdout.write(self.style.ERROR("Error setting webhook"))
        self.stdout.write(response.text)
