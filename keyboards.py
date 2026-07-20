from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():

    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton(
            "📚 دوره‌ها",
            callback_data="courses"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "💬 حرف بزنیم",
            callback_data="advisor"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "⭐ امتیاز و نظر",
            callback_data="feedback"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🏛 آکادمی آرَک",
            callback_data="about_arc"
        )
    )

    return markup


def back_to_main():

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "🏠 منوی اصلی",
            callback_data="main_menu"
        )
    )

    return markup


def rating_keyboard():

    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton("⭐", callback_data="rate_1")
    )

    markup.add(
        InlineKeyboardButton("⭐⭐", callback_data="rate_2")
    )

    markup.add(
        InlineKeyboardButton("⭐⭐⭐", callback_data="rate_3")
    )

    markup.add(
        InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rate_4")
    )

    markup.add(
        InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rate_5")
    )

    markup.add(
        InlineKeyboardButton(
            "🏠 منوی اصلی",
            callback_data="main_menu"
        )
    )

    return markup


def rating_confirm_keyboard(rating):

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "✅ تأیید امتیاز",
            callback_data=f"confirm_rate_{rating}"
        ),
        InlineKeyboardButton(
            "🔄 انتخاب دوباره",
            callback_data="feedback"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "🏠 منوی اصلی",
            callback_data="main_menu"
        )
    )

    return markup


def admin_close_btn(user_id):

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "🔒 بستن تیکت",
            callback_data=f"admin_close:{user_id}"
        )
    )

    return markup


def admin_panel():

    markup = InlineKeyboardMarkup(row_width=2)

    markup.add(
        InlineKeyboardButton(
            "📢 ارسال همگانی",
            callback_data="broadcast"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "👥 مدیریت کاربران",
            callback_data="users_panel"
        )
    )

    markup.add(
        InlineKeyboardButton(
            "📤 دانلود کاربران",
            callback_data="download_users"
        )
    )

    return markup

def closed_ticket_keyboard():

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "🏠 بازگشت به منوی اصلی",
            callback_data="main_menu"
        )
    )

    return markup
