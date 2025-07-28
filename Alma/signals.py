import telegram
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_code(code, phone):
    try:
        msg = f"📱 Номер: {phone}\n🔐 Код подтверждения: {code}"
        bot = telegram.Bot(token=BOT_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print("✅ Код успешно отправлен")
    except Exception as e:
        print(f"❌ Ошибка отправки Telegram-кода: {e}")


