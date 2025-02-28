from flask import Flask
import telebot
import tweepy
import os
from dotenv import load_dotenv
from threading import Thread

# إنشاء تطبيق Flask
app = Flask(__name__)

# تحميل متغيرات البيئة
load_dotenv()

# مفاتيح تيليجرام
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

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
HASHTAGS = "#abdullah_streams دوري_روشن"

# استقبال الرسائل من القناة
@bot.channel_post_handler(content_types=['text', 'photo', 'video'])
def handle_channel_message(message):
    if message.chat.username == CHANNEL_USERNAME.lstrip('@'):
        caption = message.caption if message.caption else message.text
        tweet_text = f"{caption}\\n\\nتابع الحساب الأساسي: @koora_ahli\\nتابع الحساب الأساسي: @a7_be7\\n\\n{HASHTAGS}"
        
        if message.photo or message.video:
            file_id = message.photo[-1].file_id if message.photo else message.video.file_id
            file_info = bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
            
            twitter_api.update_status_with_media(status=tweet_text, filename=file_url)
        else:
            twitter_api.update_status(status=tweet_text)
        
        bot.send_message(message.chat.id, "✅ تم نشر التغريدة بنجاح!")

# تشغيل البوت في Thread حتى لا يتوقف Flask
def run_bot():
    bot.polling(none_stop=True)

Thread(target=run_bot).start()

# تشغيل Flask لتفادي إيقاف Render
@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)