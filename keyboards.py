from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():

    markup = InlineKeyboardMarkup(row_width=2)

    markup.row(
        InlineKeyboardButton("📚 دوره‌ها", callback_data="courses"),
        InlineKeyboardButton("⭐️ نظر شما", callback_data="feedback")
    )

    markup.row(
        InlineKeyboardButton("👩🏻‍🏫 مشاوره", callback_data="advisor")
    )

    return markup


def admin_close_btn(user_id):

    markup = InlineKeyboardMarkup()

    markup.add(
        InlineKeyboardButton(
            "🔒 بستن تیکت",
            callback_data=f"close_ticket:{user_id}"
        )
    )

    return markup
