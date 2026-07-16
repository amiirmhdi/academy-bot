from telebot import types

def main_menu():

    markup = types.InlineKeyboardMarkup()

    btn1 = types.InlineKeyboardButton("🎓 ثبت نام", callback_data="register")
    btn2 = types.InlineKeyboardButton("📚 دوره ها", callback_data="courses")
    btn3 = types.InlineKeyboardButton("👩🏻‍🏫 مشاوره", callback_data="advisor")
    btn4 = types.InlineKeyboardButton("📞 ارتباط با ما", callback_data="contact")

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)

    return markup
