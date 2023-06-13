from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton


how_to_btn = InlineKeyboardButton("Как понять, что курс подходит мне?", callback_data="*pq")
how_to_keyboard = InlineKeyboardMarkup().add(how_to_btn)

lets_go_btn = InlineKeyboardButton("Поехали🚀", callback_data="*lg")
lets_go_keyboard = InlineKeyboardMarkup().add(lets_go_btn)

yes_btn = InlineKeyboardButton("Да✅", callback_data="*y")
no_btn = InlineKeyboardButton("Нет❌", callback_data="*n")
answer_keyboard = InlineKeyboardMarkup(row_width=2).row(yes_btn, no_btn)

yes_btn_2 = InlineKeyboardButton("Да✅", callback_data="*2y")
no_btn_2 = InlineKeyboardButton("Нет❌", callback_data="*2n")
answer_keyboard_2 = InlineKeyboardMarkup(row_width=2).row(yes_btn_2, no_btn_2)

yes_btn_3 = InlineKeyboardButton("Да✅", callback_data="*3y")
no_btn_3 = InlineKeyboardButton("Нет❌", callback_data="*3n")
answer_keyboard_3 = InlineKeyboardMarkup(row_width=2).row(yes_btn_3, no_btn_3)

yes_btn_4 = InlineKeyboardButton("Да✅", callback_data="*4y")
no_btn_4 = InlineKeyboardButton("Нет❌", callback_data="*4n")
answer_keyboard_4 = InlineKeyboardMarkup(row_width=2).row(yes_btn_4, no_btn_4)

yes_btn_5 = InlineKeyboardButton("Да✅", callback_data="*5y")
no_btn_5 = InlineKeyboardButton("Нет❌", callback_data="*5n")
answer_keyboard_5 = InlineKeyboardMarkup(row_width=2).row(yes_btn_5, no_btn_5)

yes_btn_6 = InlineKeyboardButton("Да✅", callback_data="*6y")
no_btn_6 = InlineKeyboardButton("Нет❌", callback_data="*6n")
answer_keyboard_6 = InlineKeyboardMarkup(row_width=2).row(yes_btn_6, no_btn_6)


# sign_up_btn = InlineKeyboardButton("Записаться📌", callback_data="*sign_up")
# sign_up_keyboard = InlineKeyboardMarkup().add(sign_up_btn)

sign_up_reply_btn = KeyboardButton("Записаться📌", request_contact=True)
other_services_btn = KeyboardButton("Другие услуги📝")
sign_up_reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(sign_up_reply_btn, other_services_btn)

sign_up_for_consulting_btn = KeyboardButton("Записаться на консультацию✏")
sign_up_for_course_btn = KeyboardButton("Записаться на курс📌")
get_astro_map_btn = KeyboardButton("Заказать натальную карту🔮")
services_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(sign_up_for_course_btn, sign_up_for_consulting_btn).add(get_astro_map_btn)

confirm_btn = InlineKeyboardButton("Подтвердить✅", callback_data="$confirm")
reject_btn = InlineKeyboardButton("Отклонить❌", callback_data="$refuse")
ban_btn = InlineKeyboardButton("Забанить пользователя💀", callback_data="$ban_user")
check_keyboard = InlineKeyboardMarkup().row(confirm_btn, reject_btn).add(ban_btn)

confirmed_btn = InlineKeyboardButton("Подтверждено✅", callback_data="#c")
confirmed_keyboard = InlineKeyboardMarkup().add(confirmed_btn)

rejected_btn = InlineKeyboardButton("Отклонено❌", callback_data="#r")
rejected_keyboard = InlineKeyboardMarkup().add(rejected_btn)

unban_btn = InlineKeyboardButton("Разбанить пользователя😇", callback_data="$unban_user")
unban_keyboard = InlineKeyboardMarkup().add(unban_btn)

unbanned_btn = InlineKeyboardButton("Пользователь разбанен😇", callback_data="#u")
unbanned_keyboard = InlineKeyboardMarkup().add(unbanned_btn)

video_link = InlineKeyboardButton("Уйти с нелюбимой работы?", url="https://www.youtube.com/watch?v=kxW0XvxQYZk")
link_keyboard = InlineKeyboardMarkup().add(video_link)

