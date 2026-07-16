from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    markup = InlineKeyboardMarkup(row_width=1)

    markup.add(
        InlineKeyboardButton("📚 دوره‌ها", callback_data="courses")
    )

    markup.add(
        InlineKeyboardButton("👩🏻‍🏫 مشاوره", callback_data="advisor")
    )

    markup.add(
        InlineKeyboardButton("⭐ نظر شما", callback_data="feedback")
    )

    return markup
