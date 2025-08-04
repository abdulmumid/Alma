import telegram
import os
from dotenv import load_dotenv
import qrcode
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from io import BytesIO
from django.core.files import File
import logging

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

logger = logging.getLogger(__name__)

def send_telegram_code(code, phone):
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены")
        return
    try:
        msg = f"📱 Номер: {phone}\n🔐 Код подтверждения: {code}"
        bot = telegram.Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=msg)
        logger.info("✅ Код успешно отправлен в Telegram")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки Telegram-кода: {e}")


@receiver(post_save, sender=User)
def generate_qr_code(sender, instance, created, **kwargs):
    if created and not instance.qr_code:
        qr_data = f"User: {instance.user.phone}"  # или другая уникальная информация
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        filename = f'{instance.user.phone}_qr.png'
