import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Logging ayarlarını yapıyoruz, Vercel loglarında hataları görmek için çok önemli.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Hassas bilgileri kodun içinden değil, Vercel'e gireceğimiz ortam değişkenlerinden alıyoruz.
TELEGRAM_TOKEN = os.environ.get(7875616181:AAGVLEZzYXMxRE62GC19TBdJOO_h3Nf0dQk)
CALLMEBOT_APIKEY = os.environ.get(6105401)
CALLMEBOT_PHONE = os.environ.get(+905547435696)
TARGET_CHANNEL_USERNAME = os.environ.get('TARGET_CHANNEL_USERNAME', 'onual_firsat')

# Filtrelemek istediğimiz ifadeler
FILTER_PHRASES = [
    "(Son 1 Yılın En Düşük Fiyatı)",
    "(Son 6 Ayın En Düşük Fiyatı)"
]

async def process_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gelen kanal gönderisini işleyen ana fonksiyon"""
    try:
        channel_post = update.channel_post
        
        # Eğer mesaj veya başlık yoksa işlemi durdur
        if not channel_post or not (channel_post.text or channel_post.caption):
            return

        message_text = channel_post.text or channel_post.caption
        channel_username = channel_post.chat.username

        logging.info(f"Yeni mesaj alındı: Kanal={channel_username}, Mesaj='{message_text[:50]}...'")

        # Kanal adı ve mesaj içeriği filtrelerini kontrol et
        if channel_username == TARGET_CHANNEL_USERNAME and any(phrase in message_text for phrase in FILTER_PHRASES):
            logging.info("Filtreye uyan mesaj bulundu! WhatsApp bildirimi gönderiliyor...")
            
            # CallMeBot'a istek gönder
            url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&text={requests.utils.quote(message_text)}&apikey={CALLMEBOT_APIKEY}"
            response = requests.get(url)
            
            logging.info(f"CallMeBot API cevabı: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"Bir hata oluştu: {e}", exc_info=True)


# Vercel'de çalışacak olan ana uygulama
# python-telegram-bot v20+ bu şekilde anlık (webhook) çalışır.
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Sadece kanal gönderilerini dinlemesi için bir handler ekliyoruz
application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, process_channel_post))