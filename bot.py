import telebot

from keyboards import main_menu, admin_close_btn, admin_panel
from config import TOKEN, ADMIN_ID
from database import (
    init_db,
    add_user,
    get_all_users,
    get_open_ticket,
    create_ticket,
    close_ticket,
    save_message
)

bot = telebot.TeleBot(TOKEN)

reply_map = {}

feedback_reply_map = {}

init_db()


@bot.message_handler(commands=["start"])
def start(message):

    add_user(
        message.chat.id,
        message.from_user.first_name,
        message.from_user.username
    )

    if message.chat.id == ADMIN_ID:

        bot.send_message(
            message.chat.id,
            "🛠 پنل مدیریت",
            reply_markup=admin_panel()
        )

        return

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

    elif call.data == "broadcast":

        msg = bot.send_message(
            call.message.chat.id,
            "📢 پیام همگانی را ارسال کنید."
        )

        bot.register_next_step_handler(
            msg,
            broadcast_message
        )

    elif call.data.startswith("admin_close:"):

        user_id = int(call.data.split(":")[1])

        close_ticket(user_id)

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )

        bot.send_message(
            user_id,
            "✅ گفتگوی شما توسط مشاور بسته شد.\n\nبرای شروع مجدد روی 👩🏻‍🏫 مشاوره بزنید."
        )

        bot.answer_callback_query(
            call.id,
            "✅ تیکت بسته شد."
        )   

def send_to_admin(message, ticket_id):

    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "ندارد"
    )

    info = bot.send_message(
        ADMIN_ID,
        f"""🎫 تیکت #{ticket_id}

👤 {message.from_user.first_name}
🆔 {username}
📌 USER_ID:{message.chat.id}""",
        reply_markup=admin_close_btn(message.chat.id)
    )

    reply_map[info.message_id] = message.chat.id

    if message.content_type == "text":

        sent = bot.send_message(
            ADMIN_ID,
            message.text,
            reply_to_message_id=info.message_id
        )

    else:

        sent = bot.forward_message(
            ADMIN_ID,
            message.chat.id,
            message.message_id
        )

    reply_map[sent.message_id] = message.chat.id

    bot.send_message(
        message.chat.id,
        "✅ پیام شما برای مشاور ارسال شد."
    )

@bot.message_handler(
    func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message,
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation",
        "sticker",
        "video_note"
    ]
)
def admin_reply(message):

    reply_id = message.reply_to_message.message_id

    # پاسخ به نظرسنجی
    if reply_id in feedback_reply_map:

        user_id = feedback_reply_map[reply_id]

        if message.content_type == "text":

            bot.send_message(
                user_id,
                f"💬 پاسخ آکادمی:\n\n{message.text}"
            )

        else:

            bot.copy_message(
                chat_id=user_id,
                from_chat_id=ADMIN_ID,
                message_id=message.message_id
            )

        bot.reply_to(
            message,
            "✅ پاسخ ارسال شد."
        )

        return

    # پاسخ به تیکت
    if reply_id not in reply_map:
        bot.reply_to(
            message,
            "❌ روی پیام کاربر ریپلای کنید."
        )
        return

    user_id = reply_map[reply_id]

    if (
        message.content_type == "text"
        and message.text.strip() == "/close"
    ):

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

    if message.content_type == "text":

        bot.send_message(
            user_id,
            f"👩🏻‍🏫 مشاور:\n\n{message.text}"
        )

    else:

        bot.copy_message(
            chat_id=user_id,
            from_chat_id=ADMIN_ID,
            message_id=message.message_id
        )

    bot.reply_to(
        message,
        "✅ ارسال شد."
    )

@bot.message_handler(
    func=lambda m: m.chat.id != ADMIN_ID,
    content_types=["text"]
)
def user_chat(message):

    ticket = get_open_ticket(message.chat.id)

    if not ticket:
        return

    send_to_admin(
        message,
        ticket[0]
    )

def send_feedback(message):

    username = (
        "@" + message.from_user.username
        if message.from_user.username
        else "ندارد"
    )

    text = f'''⭐ نظر جدید

"{message.from_user.first_name}"
{username}

💬
{message.text}'''

    info = bot.send_message(
        ADMIN_ID,
        text
    )

    feedback_reply_map[info.message_id] = message.chat.id

    bot.send_message(
        message.chat.id,
        "❤️ ممنون، نظر شما ثبت شد."
    )
@bot.message_handler(
    func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message,
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "voice",
        "animation",
        "sticker",
        "video_note"
    ]
)
def admin_feedback_reply(message):

    reply_id = message.reply_to_message.message_id

    if reply_id not in feedback_reply_map:
        return

    user_id = feedback_reply_map[reply_id]

    if message.content_type == "text":

        bot.send_message(
            user_id,
            f"💬 پاسخ ادمین:\n\n{message.text}"
        )

    else:

        bot.copy_message(
            chat_id=user_id,
            from_chat_id=ADMIN_ID,
            message_id=message.message_id
        )

    bot.reply_to(
        message,
        "✅ پاسخ ارسال شد."
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

    if message.chat.id == ADMIN_ID:
        return

    ticket = get_open_ticket(message.chat.id)

    if not ticket:
        return

    send_to_admin(
        message,
        ticket[0]
    )

def broadcast_message(message):

    users = get_all_users()

    print("=" * 50)
    print("USERS:", users)
    print("TOTAL USERS:", len(users))
    print("=" * 50)

    success = 0
    failed = 0

    for user in users:

        chat_id = user[0]

        try:

            print(f"Sending to: {chat_id}")

            if message.content_type == "text":

                bot.send_message(
                    chat_id,
                    message.text
                )

            else:

                bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )

            print(f"SUCCESS -> {chat_id}")
            success += 1

        except Exception as e:

            print(f"FAILED -> {chat_id}")
            print(e)
            failed += 1

    print("=" * 50)
    print(f"SUCCESS: {success}")
    print(f"FAILED: {failed}")
    print("=" * 50)

    bot.send_message(
        ADMIN_ID,
        f"""✅ ارسال همگانی پایان یافت.

📤 موفق: {success}
❌ ناموفق: {failed}"""
    )

    
print("Bot Started...")

bot.infinity_polling(skip_pending=True)    
