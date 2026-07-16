import telebot

from keyboards import main_menu
from config import TOKEN, ADMIN_ID
from database import (
    init_db,
    add_user,
    get_open_ticket,
    create_ticket,
    close_ticket
)

bot = telebot.TeleBot(TOKEN)

init_db()


@bot.message_handler(commands=["start"])
def start(message):

    add_user(
        message.chat.id,
        message.from_user.first_name,
        message.from_user.username
    )

    bot.send_message(
        message.chat.id,
        "🎓 به آکادمی آرک خوش آمدید.\n\nیکی از گزینه‌های زیر را انتخاب کنید.",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    bot.answer_callback_query(call.id)

    if call.data == "courses":

        bot.send_message(
            call.message.chat.id,
            "📚 لیست دوره‌ها به زودی اضافه می‌شود."
        )

    elif call.data == "advisor":

        ticket = get_open_ticket(call.message.chat.id)

        if ticket:
            ticket_id = ticket[0]
        else:
            ticket_id = create_ticket(call.message.chat.id)

        msg = bot.send_message(
            call.message.chat.id,
            "💬 پیام خود را بنویسید."
        )

        bot.register_next_step_handler(
            msg,
            send_to_admin,
            ticket_id
        )

    elif call.data == "feedback":

        msg = bot.send_message(
            call.message.chat.id,
            "⭐ لطفاً نظر خود را بنویسید."
        )

        bot.register_next_step_handler(
            msg,
            send_feedback
        )   

def send_to_admin(message, ticket_id):

    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "ندارد"
    )

    caption = f"""🎫 تیکت #{ticket_id}

👤 {message.from_user.first_name}
🆔 {username}
📌 USER_ID:{message.chat.id}
"""

    if message.content_type == "text":

        bot.send_message(
            ADMIN_ID,
            f"{caption}\n\n💬\n{message.text}"
        )

    else:

        bot.forward_message(
            ADMIN_ID,
            message.chat.id,
            message.message_id
        )

        bot.send_message(
            ADMIN_ID,
            caption
        )

    bot.send_message(
        message.chat.id,
        "✅ پیام شما برای مشاور ارسال شد."
    )

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message)
def admin_reply(message):

    reply_text = message.reply_to_message.text

    if "USER_ID:" not in reply_text:
        bot.reply_to(
            message,
            "❌ این پیام متعلق به کاربر نیست."
        )
        return

    user_id = int(
        reply_text.split("USER_ID:")[1].split("\n")[0]
    )

    if message.content_type == "text":

        if message.text.strip() == "/close":

            close_ticket(user_id)

            bot.send_message(
                user_id,
                "✅ گفتگوی شما بسته شد.\n\nبرای شروع مجدد روی 👩🏻‍🏫 مشاوره بزنید."
            )

            bot.reply_to(
                message,
                "✅ تیکت بسته شد."
            )

            return

        bot.send_message(
            user_id,
            f"👩🏻‍🏫 مشاور:\n\n{message.text}"
        )

    else:

        bot.forward_message(
            user_id,
            ADMIN_ID,
            message.message_id
        )

    bot.reply_to(
        message,
        "✅ ارسال شد."
    )

@bot.message_handler(func=lambda message: True)
def user_chat(message):

    if message.chat.id == ADMIN_ID:
        return

    ticket = get_open_ticket(message.chat.id)

    if not ticket:
        return

    ticket_id = ticket[0]

    send_to_admin(
        message,
        ticket_id
    )

def send_feedback(message):

    username = message.from_user.username

    if username:
        username = "@" + username
    else:
        username = "ندارد"

    text = f"""
⭐ نظر جدید

👤 {message.from_user.first_name}
🆔 {username}

💬
{message.text}
"""

    bot.send_message(
        ADMIN_ID,
        text
    )

    bot.send_message(
        message.chat.id,
        "❤️ ممنون، نظر شما ثبت شد."
    )

@bot.message_handler(content_types=[
    "photo",
    "video",
    "document",
    "audio",
    "voice",
    "animation",
    "sticker",
    "video_note"
])
def media_handler(message):

    ticket = get_open_ticket(message.chat.id)

    if not ticket:
        return

    ticket_id = ticket[0]

    bot.forward_message(
        ADMIN_ID,
        message.chat.id,
        message.message_id
    )

    reply_map[message.message_id] = (
        message.chat.id,
        ticket_id
    )

    
print("Bot Started...")

bot.infinity_polling(skip_pending=True)    
