import os
import logging
import json
import requests
from http.server import BaseHTTPRequestHandler

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Ortam Değişkenlerini alıyoruz (SADECE İSİMLERİYLE)
try:
    # KODUN BU KISMINA KESİNLİKLE DOKUNMAYIN
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CALLMEBOT_APIKEY = os.environ['CALLMEBOT_APIKEY']
    CALLMEBOT_PHONE = os.environ['CALLMEBOT_PHONE']
    TARGET_CHANNEL_USERNAME = os.environ.get('TARGET_CHANNEL_USERNAME', 'onual_firsat')
except KeyError as e:
    logging.error(f"Zorunlu ortam değişkeni eksik: {e}")
    raise

# Filtrelemek istediğimiz ifadeler
FILTER_PHRASES = [
    "(Son 1 Yılın En Düşük Fiyatı)",
    "(Son 6 Ayın En Düşük Fiyatı)"
]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            update_data = json.loads(body.decode('utf-8'))
            logging.info(f"Gelen veri: {update_data}")

            if 'channel_post' in update_data:
                channel_post = update_data['channel_post']
                message_text = channel_post.get('text') or channel_post.get('caption')
                channel_username = channel_post.get('chat', {}).get('username')

                if message_text and channel_username:
                    logging.info(f"Yeni mesaj: Kanal={channel_username}, Mesaj='{message_text[:50]}...'")
                    if channel_username == TARGET_CHANNEL_USERNAME and any(phrase in message_text for phrase in FILTER_PHRASES):
                        logging.info("Filtreye uyan mesaj bulundu! WhatsApp bildirimi gönderiliyor...")
                        safe_message_text = requests.utils.quote(message_text)
                        url = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&text={safe_message_text}&apikey={CALLMEBOT_APIKEY}"
                        response = requests.get(url, timeout=10)
                        logging.info(f"CallMeBot API cevabı: {response.status_code} - {response.text}")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            logging.error(f"POST isteği işlenirken bir hata oluştu: {e}", exc_info=True)
            self.send_response(500)
            self.end_headers()
        return

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Telegram Firsat Bot Webhook'u calisiyor.")
        return