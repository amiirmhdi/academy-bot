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
            "🏛 آکادمی آرک",
            callback_data="about_arc"
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
