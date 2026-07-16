from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)

    markup.row(
        InlineKeyboardButton("📚 دوره‌ها", callback_data="courses"),
        InlineKeyboardButton("⭐ نظر شما", callback_data="feedback")
    )

    markup.row(
        InlineKeyboardButton("👩🏻‍🏫 مشاوره", callback_data="advisor")
    )

    return markup
