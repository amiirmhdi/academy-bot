from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.row(
        InlineKeyboardButton("📚 دوره‌ها", callback_data="courses"),
        InlineKeyboardButton("👩🏻‍🏫 مشاوره", callback_data="advisor")
    )

    markup.row(
        InlineKeyboardButton("⭐ نظر شما", callback_data="feedback")
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
