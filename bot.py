import telebot
import os
from datetime import datetime
import threading
from flask import Flask, request

# توكن البوت
API_TOKEN = '7534795874:AAGehbCQR8h82qcNI1zabmFYdqg3satj4ag'
bot = telebot.TeleBot(API_TOKEN)

# معرف المطور
ADMIN_ID = 7601607055

# إعداد Flask
server = Flask(__name__)

# قائمة الأذكار
dhikr_list = [
    {"text": "سبحان الله", "pdf": None},
    {"text": "الحمد لله", "pdf": None},
    {"text": "الله أكبر", "pdf": None},
]

# لتخزين حالة التفعيل
active_chats = {}

# قائمة المهام المجدولة
scheduled_tasks = []

# لوحة التحكم
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("إضافة ذكر جديد", "عرض قائمة الأذكار")
        markup.add("جدولة ذكر", "عرض المهام المجدولة")
        markup.add("تفعيل البوت", "إيقاف البوت")
        bot.send_message(message.chat.id, "مرحبًا بك في لوحة التحكم! اختر خيارًا:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "عذرًا، هذه الميزة متاحة فقط للمطور.")

# إضافة ذكر جديد مع إمكانية إرفاق ملف PDF
@bot.message_handler(func=lambda message: message.text == "إضافة ذكر جديد")
def add_dhikr_prompt(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "أرسل الذكر الذي تريد إضافته:")
        bot.register_next_step_handler(message, add_dhikr)
    else:
        bot.send_message(message.chat.id, "عذرًا، هذه الميزة متاحة فقط للمطور.")

def add_dhikr(message):
    if message.chat.id == ADMIN_ID:
        new_dhikr = message.text.strip()
        bot.send_message(message.chat.id, "هل تريد إرفاق ملف PDF مع هذا الذكر؟ (أرسل الملف الآن أو اكتب 'لا')")
        bot.register_next_step_handler(message, lambda m: attach_pdf(m, new_dhikr))
    else:
        bot.send_message(message.chat.id, "عذرًا، هذه الميزة متاحة فقط للمطور.")

def attach_pdf(message, dhikr):
    if message.content_type == 'document':
        file_id = message.document.file_id
        dhikr_list.append({"text": dhikr, "pdf": file_id})
        bot.send_message(message.chat.id, "تمت إضافة الذكر مع الملف بنجاح!")
    elif message.text.lower() == 'لا':
        dhikr_list.append({"text": dhikr, "pdf": None})
        bot.send_message(message.chat.id, "تمت إضافة الذكر بدون ملف.")
    else:
        bot.send_message(message.chat.id, "لم يتم التعرف على الملف. يرجى المحاولة مرة أخرى.")

# عرض قائمة الأذكار
@bot.message_handler(func=lambda message: message.text == "عرض قائمة الأذكار")
def show_dhikr_list(message):
    if message.chat.id == ADMIN_ID:
        if dhikr_list:
            response = "قائمة الأذكار الحالية:\n"
            for i, dhikr in enumerate(dhikr_list, 1):
                response += f"{i}. {dhikr['text']}\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "لا توجد أذكار حاليًا.")
    else:
        bot.send_message(message.chat.id, "عذرًا، هذه الميزة متاحة فقط للمطور.")

# جدولة ذكر معين
@bot.message_handler(func=lambda message: message.text == "جدولة ذكر")
def schedule_dhikr_prompt(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "أرسل الذكر الذي تريد جدولته:")
        bot.register_next_step_handler(message, get_dhikr_time)
    else:
        bot.send_message(message.chat.id, "عذرًا، هذه الميزة متاحة فقط للمطور.")

def get_dhikr_time(message):
    dhikr = message.text.strip()
    bot.send_message(message.chat.id, "أرسل الوقت بصيغة (ساعة:دقيقة) مثل 07:00:")
    bot.register_next_step_handler(message, lambda m: schedule_time(m, dhikr))

def schedule_time(message, dhikr):
    time_str = message.text.strip()
    try:
        hour, minute = map(int, time_str.split(":"))
        scheduled_tasks.append({"text": dhikr, "hour": hour, "minute": minute})
        bot.send_message(message.chat.id, f"تمت جدولة الذكر '{dhikr}' الساعة {time_str}.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة الوقت غير صحيحة. يرجى المحاولة مرة أخرى.")

# عرض المهام المجدولة
@bot.message_handler(func=lambda message: message.text == "عرض المهام المجدولة")
def show_scheduled_tasks(message):
    if message.chat.id == ADMIN_ID:
        if scheduled_tasks:
            response = "المهام المجدولة:\n"
            for task in scheduled_tasks:
                response += f"- {task['text']} (الساعة: {task['hour']}:{task['minute']:02d})\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "لا توجد مهام مجدولة.")
    else:
        bot.send_message(message.chat.id, "عذرًا، هذه الميزة متاحة فقط للمطور.")

# إرسال الأذكار بشكل دوري
def check_scheduled_tasks():
    while True:
        now = datetime.now()
        for task in scheduled_tasks:
            if task['hour'] == now.hour and task['minute'] == now.minute:
                bot.send_message(ADMIN_ID, task['text'])
                time.sleep(60)  # تفادي التكرار خلال الدقيقة
        time.sleep(30)

threading.Thread(target=check_scheduled_tasks).start()

# نقطة نهاية Flask
@server.route('/' + API_TOKEN, methods=['POST'])
def get_updates():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
bot.set_webhook(url="https://dww-5t0x.onrender.com/" + API_TOKEN)

    return "Webhook is set!", 200

# بدء السيرفر
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
