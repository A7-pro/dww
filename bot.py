from flask import Flask
import telebot
import tweepy
import os
import requests
from dotenv import load_dotenv
from threading import Thread

# إنشاء تطبيق Flask
app = Flask(__name__)

# تحميل متغيرات البيئة
load_dotenv()

# مفاتيح تيليجرام
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USER_ID = os.getenv("USER_ID")  # ID المستخدم بدلاً من القناة

# مفاتيح تويتر
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# إعداد تويتر API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

# إعداد تيليجرام API
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# هاشتاقات ثابتة
HASHTAGS = "#الأهلي #AlAhli #دوري_روشن"

# أمر /start للترحيب بالمستخدمين
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً وسهلاً! هذا البوت يقوم بنشر رسائلك تلقائيًا على تويتر.\n\n"
                          "📌 فقط أرسل رسالة هنا، وسيتم نشرها على تويتر تلقائيًا ✅")

# تصحيح لاستقبال الرسائل الخاصة فقط
@bot.message_handler(func=lambda message: True)
def debug_message(message):
    bot.reply_to(message, f"📌 استلمت رسالتك!\n🔹 ID الخاص بك: {message.chat.id}")
    if str(message.chat.id) != USER_ID:
        bot.reply_to(message, "🚫 هذا البوت مخصص لحساب معين فقط!")
        return
    
    caption = message.caption if message.caption else message.text
    tweet_text = f"{caption}\n\nتابع الحساب الأساسي: @koora_ahli\nتابع الحساب الأساسي: @a7_be7\n\n{HASHTAGS}"
    
    try:
        if message.photo or message.video:
            file_id = message.photo[-1].file_id if message.photo else message.video.file_id
            file_info = bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
            file_path = "media.mp4" if message.video else "media.jpg"

            # تحميل الملف من تيليجرام وحفظه بشكل دائم
            with open(file_path, 'wb') as f:
                f.write(requests.get(file_url).content)

            # نشر التغريدة مع الميديا
            twitter_api.update_status_with_media(status=tweet_text, filename=file_path)
        else:
            twitter_api.update_status(status=tweet_text)
        
        bot.send_message(message.chat.id, "✅ تم نشر التغريدة بنجاح!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ أثناء النشر على تويتر: {e}")

# تشغيل البوت في Thread حتى لا يتوقف Flask
def run_bot():
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

Thread(target=run_bot).start()

# تشغيل Flask لتفادي إيقاف Render
@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
