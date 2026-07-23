import os
import telebot
from openpyxl import Workbook

from keyboards import (
    main_menu,
    back_to_main,
    closed_ticket_keyboard,
    admin_close_btn,
    admin_panel,
    rating_keyboard,
    rating_confirm_keyboard
)
from config import TOKEN, ADMIN_ID
from database import (
    init_db,
    add_user,
    get_all_users,
    get_open_ticket,
    create_ticket,
    close_ticket,
    save_message,
    get_users_count,
    get_first_user,
    get_last_user,
    get_users_info,
    save_rating,
    save_review,
    get_rating_stats,
    get_connection
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

    if call.data == "main_menu":

        bot.clear_step_handler_by_chat_id(call.message.chat.id)

        prompt_id = reply_map.get(f"prompt_{call.message.chat.id}")

        if prompt_id:
            try:
                bot.delete_message(call.message.chat.id, prompt_id)
                del reply_map[f"prompt_{call.message.chat.id}"]
            except:
                pass

        close_ticket(call.message.chat.id)

        bot.edit_message_text(
            """🎓 آکادمی آرَک

یکی از گزینه‌های زیر را انتخاب کنید.""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=main_menu()
        )

        return

    elif call.data == "courses":

        bot.edit_message_text(
            """📚 دوره‌ها

لیست دوره‌های آکادمی آرَک به زودی اضافه می‌شود.

🌱 منتظر خبرهای خوب باشید.""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_to_main()
        )

    elif call.data == "advisor":

        ticket = get_open_ticket(call.message.chat.id)

        if ticket:
            ticket_id = ticket[0]
        else:
            ticket_id = create_ticket(call.message.chat.id)

        bot.edit_message_text(
            """💬 حرف بزنیم

پیام خود را برای مشاور ارسال کنید.

در اولین فرصت پاسخ شما داده خواهد شد.""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_to_main()
        )

        msg = bot.send_message(
            call.message.chat.id,
            "✍️ پیام خود را ارسال کنید:"
        )

        reply_map[f"prompt_{call.message.chat.id}"] = msg.message_id

        bot.register_next_step_handler(
            msg,
            send_to_admin,
            ticket_id
        )


    elif call.data == "feedback":

        bot.edit_message_text(
            """⭐️ امتیاز و نظر

لطفاً میزان رضایت خود از آکادمی آرَک را انتخاب کنید.""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=rating_keyboard()
        )


    elif call.data.startswith("rate_"):

        rating = int(call.data.split("_")[1])

        stars = "⭐️" * rating

        bot.edit_message_text(
            f"""⭐️ شما به آکادمی آرَک

{stars}

امتیاز دادید.

آیا از انتخاب خود مطمئن هستید؟""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=rating_confirm_keyboard(rating)
        )


    elif call.data.startswith("confirm_rate_"):

        rating = int(call.data.split("_")[2])

        save_rating(
            call.from_user.id,
            call.from_user.first_name,
            call.from_user.username,
            rating
        )

        msg = bot.send_message(
            call.message.chat.id,
            """❤️ از اینکه برای بهتر شدن آکادمی آرَک وقت گذاشتی، ممنونیم.

اگر دوست داشتی،
نظر یا پیشنهادت رو هم برامون بنویس.

🌱 نظرات شما کمک می‌کنه هر روز بهتر از قبل باشیم.

(نوشتن نظر کاملاً اختیاری است.)"""
        )

        bot.register_next_step_handler(
            msg,
            send_feedback
        )


    elif call.data == "about_arc":

        bot.edit_message_text(
            """🏛 آکادمی آرَک

«آرَک» در فارسی کهن به معنای «آسمان بلند» و «بالا» آمده و در برخی متون قدیمی مفاهیمی مانند «افتخار» و «شکوه» را تداعی می‌کند.

ما باور داریم یادگیری یعنی حرکت به سمت جایگاهی بالاتر؛ مسیری برای رشد، پیشرفت و ساختن آینده‌ای بهتر.

آکادمی آرَک تازه ابتدای این مسیر است. هدف ما فقط محدود به تلگرام نیست و در آینده با توسعه امکانات، دوره‌ها و پلتفرم اختصاصی، محیطی کامل‌تر برای یادگیری ایجاد خواهیم کرد.

از اینکه همراه ما هستی خوشحالیم. ❤️""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_to_main()
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


    elif call.data == "users_panel":

        count = get_users_count()
        first = get_first_user()
        last = get_last_user()

        bot.send_message(
            call.message.chat.id,
            f"""👥 مدیریت کاربران

👤 تعداد کاربران: {count}

🥇 اولین کاربر:
{first}

🆕 آخرین کاربر:
{last}
"""
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
            """✅ گفتگوی شما توسط مشاور بسته شد.

اگر دوباره نیاز به مشاوره داشتید، از دکمه زیر استفاده کنید.""",
            reply_markup=closed_ticket_keyboard()
        )

        bot.answer_callback_query(
            call.id,
            "✅ گفتگوی شما بسته شد."
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

    save_review(
        message.chat.id,
        message.text
    )

    count, avg = get_rating_stats()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT rating
    FROM ratings
    WHERE chat_id=%s
    """, (message.chat.id,))

    rating = cur.fetchone()[0]

    cur.close()
    conn.close()

    stars = "⭐" * rating

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "ندارد"
    )

    bot.send_message(
        ADMIN_ID,
        f"""🌟 بازخورد جدید دریافت شد

👤 {message.from_user.first_name}

🆔 {message.chat.id}

📛 {username}

⭐ امتیاز:
{stars} ({rating} از 5)

📊 میانگین امتیاز:
{round(avg,2)} ⭐

🗳 تعداد کل رأی‌ها:
{count}

💬 نظر:

{message.text}"""
    )

    bot.send_message(
        message.chat.id,
        """❤️ ممنون بابت امتیاز و نظرت.

بازخورد شما برای بهتر شدن آکادمی آرَک
خیلی ارزشمنده. 🌱"""
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


def download_users_excel(chat_id):

    users = get_users_info()

    wb = Workbook()
    ws = wb.active
    ws.title = "Users"

    ws.append([
        "Chat ID",
        "First Name",
        "Username"
    ])

    for user in users:

        ws.append([
            user[0],
            user[1],
            user[2]
        ])

    file_name = "users.xlsx"

    wb.save(file_name)

    with open(file_name, "rb") as file:

        bot.send_document(
            chat_id,
            file,
            caption=f"👥 تعداد کاربران: {len(users)}"
        )

    os.remove(file_name)

    
print("Bot Started...")

bot.infinity_polling(skip_pending=True)    
