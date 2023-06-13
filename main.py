import asyncio
import datetime
import logging
import traceback

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from pymongo import MongoClient
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, MONGOKEY
import keyboards

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

client = MongoClient(MONGOKEY)
db = client.destiny

messages_dict = {
    "start": [
        "<b>Предназначение</b> - суть и смысл существования, дело и задача всей жизни.\nЛюди, нашедшие его, "
        "сияют, наслаждаются жизнью, приносят пользу обществу и заряжаются энергией . Они используют все свои сильные "
        "стороны, и поэтому им нет "
        "равных.\n\nКаждый из нас может найти своё призвание\nНо как это сделать?\nКуда идти?\nК кому обратиться?",
        "На все эти вопросы вы сможете найти ответы на курсе <b>\"Предназначение\"</b>, "
        "который поможет вам начать новую жизнь, разобраться со своими проблемами и увидеть свою силу"],
    "pre_question": [
        "Чтобы понять подходит ли вам курс и бесплатно получить видео-инструкцию (как уйти с нелюбимой работы), "
        "ответьте на несколько вопросов"],
    "first_question": [
        "Приходя на работу, вы не понимаете что вы здесь делаете, чувствуете постоянную усталость и понимаете, "
        "что уперлись в потолок."],
    "second_question": [
        "Вы ощущаете себя в замкнутом круге: \"Работа-Дом-Семья-Обязательства\".\nВ этой гонке вы <b>забыли свои "
        "мечты и цели</b>."],
    "third_question": ["Вы не можете понять куда двигаться дальше, <b>вас никуда не тянет</b>. Вы почти "
                       "не испытываете эмоций."],
    "fourth_question": ["Вы не можете найти понимание среди окружающих, все вокруг просто <b>\"терпят и ждут\"</b> "
                        "и ожидают от вас то же самое"],
    "fifth_question": ["Вы чувствуете, что вы больше чем просто каждодневная рутина. Но пока что просто не знаете как "
                       "найти и раскрыть свою уникальность и индивидуальность"],
    "sixth_question": ["Вы хотите просыпаться каждый день с ощущением радости, потому что нашли свой путь и "
                       "реализуете своё предназначение."],
    "invite_msg": ["Курс вам подходит, вы можете записаться на него.",
                   "Вы ненуждаетесь в данном курсе, если вы были честны с собой, но вы можете воспользоваться другими "
                   "услугами."],
    "error_msg": ["Извините, что-то пошло не так, ответьте на вопросы ещё раз🥺(/get_questions)"],
    "video": ["Ваше бесплатное видео:"]}

users_dict = {}
users_control_dict = {}


class States(StatesGroup):
    LETS_GO = State()
    FIRST = State()
    SECOND = State()
    THIRD = State()
    FOURTH = State()
    FIFTH = State()
    SIXTH = State()
    CONSULTING = State()
    COURSE = State()
    MAP = State()


def check_if_admin(message: types.Message):
    admin = False
    for elem in db.control.find({}):
        if message.from_user.id == elem["user_id"]:
            admin = True
    return admin


def check_user_exists(message: types.Message):
    admin = False
    for elem in db.users.find({}):
        if message.from_user.id == elem["user_id"]:
            admin = True
    return admin


def process_answer(callback: types.CallbackQuery):
    data = callback.data[1:]
    if len(data) > 1:
        if data == "6n":
            users_dict[callback.from_user.id] = False
        data = data[1:]
    if data == "y":
        val = None
        try:
            val = users_dict[callback.from_user.id]
        except Exception:
            users_dict[callback.from_user.id] = True
        if val is False:
            users_dict[callback.from_user.id] = True
    else:
        try:
            users_dict[callback.from_user.id]
        except Exception:
            users_dict[callback.from_user.id] = False


def get_id_from_message(message: types.Message):
    split_data = message.text.split("(")
    split_data = split_data[1].split(")")
    user_id = int(split_data[0])
    return user_id


def request_controller(user_id, param_to_control):
    user_data = db.users.find({"user_id": user_id}).limit(1)[0]
    current_param_value = user_data[param_to_control]
    date_now = datetime.datetime.today()
    if current_param_value != "":
        param_date = datetime.datetime.strptime(current_param_value, "%Y-%m-%d")
        if date_now > (param_date + datetime.timedelta(days=1)):
            return True
        else:
            return False
    else:
        return True


def update_param_in_db(user_id, param_to_control):
    date_now = datetime.datetime.today()
    db.users.update_one({"user_id": user_id}, {"$set": {param_to_control: date_now.strftime("%Y-%m-%d")}})


def is_banned(user_id):
    flag = db.users.find({"user_id": user_id}).limit(0)[0]["banned"]
    return flag


def has_contact(user_id):
    flag = db.users.find({"user_id": user_id}).limit(0)[0]["contact"]
    if isinstance(flag, bool):
        return False
    else:
        return True


def insert_user_data_in_db(user_id, phone, user_name):
    if not has_contact(user_id):
        db.users.update_one({"user_id": user_id}, {"$set": {"contact": {"phone": phone, "user_name": user_name}}})


def get_user_data(user_id):
    if has_contact(user_id):
        user_data = db.users.find({"user_id": user_id}).limit(1)[0]["contact"]
        return user_data["phone"], user_data["user_name"]


async def send_to_receiver_from_contact(user_id, username, contact, message):
    receiver = db.receiver.find({})
    for elem in receiver:
        await bot.send_message(elem["user_id"],
                               username + "(" + str(user_id) + "): " + str(contact.phone_number) + "\n" + "*" + message,
                               reply_markup=keyboards.check_keyboard)


async def send_to_receiver_from_db(user_id, message):
    receiver = db.receiver.find({})
    user = db.users.find({"user_id": user_id}).limit(1)[0]
    username = user["contact"]["user_name"]
    phone_number = user["contact"]["phone"]
    for elem in receiver:
        await bot.send_message(elem["user_id"],
                               username + "(" + str(user_id) + "): " + str(phone_number) + "\n" + "*" + message,
                               reply_markup=keyboards.check_keyboard)


def edit_category_name(text):
    if text == "Курс":
        return "курс"
    elif text == "Натальная карта":
        return "натальную карту"
    elif text == "Консультация":
        return "консультацию"


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    if not check_user_exists(message):
        db.users.insert_one(
            {"user_id": message.from_user.id, "banned": False, "course": "", "consultation": "", "astro_map": "",
             "contact": False})
    else:
        if is_banned(message.from_user.id):
            await bot.send_message(message.from_user.id, "Вы забанены🥴")
            return
    await bot.send_message(message.from_user.id, messages_dict["start"][0], parse_mode="HTML")
    await asyncio.sleep(10)
    message_to_edit = await bot.send_message(message.from_user.id, messages_dict["start"][1], parse_mode="HTML")
    await asyncio.sleep(5)
    await message_to_edit.edit_reply_markup(reply_markup=keyboards.how_to_keyboard)


@dp.callback_query_handler(lambda c: c.data[0] == "*")
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data[1:]
    users_control_dict[callback.from_user.id] = {"message_id": callback.message.message_id, "callback_data": data}
    if data == "pq":
        await States.LETS_GO.set()
        await bot.send_message(callback.from_user.id, messages_dict["pre_question"][0],
                               reply_markup=keyboards.lets_go_keyboard, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data[0] == "$")
async def admin_callbacks_handler(callback: types.CallbackQuery):
    data = callback.data[1:]
    if data == "confirm":
        await callback.message.edit_reply_markup(reply_markup=keyboards.confirmed_keyboard)
        user_id = get_id_from_message(callback.message)
        category = callback.message.text.split("*")[-1]
        adder = edit_category_name(category)
        await bot.send_message(user_id, "Ваша заявка на " + adder + " была принята🥳")
    elif data == "refuse":
        await callback.message.edit_reply_markup(reply_markup=keyboards.rejected_keyboard)
        user_id = get_id_from_message(callback.message)
        category = callback.message.text.split("*")[-1]
        adder = edit_category_name(category)
        await bot.send_message(user_id, "Ваша заявка на " + adder + " была отклонена😓")
    elif data == "ban_user":
        await callback.message.edit_reply_markup(reply_markup=keyboards.unban_keyboard)
        user_id = get_id_from_message(callback.message)
        db.users.update_one({"user_id": user_id}, {"$set": {"banned": True}})
        await bot.send_message(user_id, "Вы были забанены😑")
    elif data == "unban_user":
        await callback.message.edit_reply_markup(reply_markup=keyboards.unbanned_keyboard)
        user_id = get_id_from_message(callback.message)
        db.users.update_one({"user_id": user_id}, {"$set": {"banned": False}})
        await bot.send_message(user_id, "Вас разбанили😇")


@dp.message_handler(commands=["get_questions"])
async def get_questions_handler(message: types.Message):
    if not is_banned(message.from_user.id):
        await start_question_list(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, "Вы забанены🥴")


async def start_question_list(user_id):
    await States.FIRST.set()
    await bot.send_message(user_id, messages_dict["first_question"][0],
                           reply_markup=keyboards.answer_keyboard, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data == "*lg", state=States.LETS_GO)
async def lg_message_handler(callback: types.CallbackQuery):
    await start_question_list(callback.from_user.id)


@dp.callback_query_handler(lambda c: c.data[0] == "*", state=States.FIRST)
async def first_question_handler(callback: types.CallbackQuery):
    process_answer(callback)
    await States.SECOND.set()
    await bot.send_message(callback.from_user.id, messages_dict["second_question"][0],
                           reply_markup=keyboards.answer_keyboard_2, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data[0:2] == "*2", state=States.SECOND)
async def second_question_handler(callback: types.CallbackQuery):
    process_answer(callback)
    await States.THIRD.set()
    await bot.send_message(callback.from_user.id, messages_dict["third_question"][0],
                           reply_markup=keyboards.answer_keyboard_3, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data[0:2] == "*3", state=States.THIRD)
async def third_question_handler(callback: types.CallbackQuery):
    process_answer(callback)
    await States.FOURTH.set()
    await bot.send_message(callback.from_user.id, messages_dict["fourth_question"][0],
                           reply_markup=keyboards.answer_keyboard_4, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data[0:2] == "*4", state=States.FOURTH)
async def fourth_question_handler(callback: types.CallbackQuery):
    process_answer(callback)
    await States.FIFTH.set()
    await bot.send_message(callback.from_user.id, messages_dict["fifth_question"][0],
                           reply_markup=keyboards.answer_keyboard_5, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data[0:2] == "*5", state=States.FIFTH)
async def fifth_question_handler(callback: types.CallbackQuery):
    process_answer(callback)
    await States.SIXTH.set()
    await bot.send_message(callback.from_user.id, messages_dict["sixth_question"][0],
                           reply_markup=keyboards.answer_keyboard_6, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data[0:2] == "*6", state=States.SIXTH)
async def sixth_question_handler(callback: types.CallbackQuery, state: FSMContext):
    process_answer(callback)
    try:
        val = users_dict[callback.from_user.id]
        if val:
            await bot.send_message(callback.from_user.id, messages_dict["invite_msg"][0],
                                                  reply_markup=keyboards.sign_up_reply_keyboard)
            await bot.send_message(callback.from_user.id, messages_dict["video"][0],
                                   reply_markup=keyboards.link_keyboard)

        else:
            await bot.send_message(callback.from_user.id, messages_dict["invite_msg"][1],
                                   reply_markup=keyboards.services_keyboard)
        await state.reset_state()
    except KeyError:
        await state.reset_state()
        await bot.send_message(callback.from_user.id, messages_dict["error_msg"][0],
                               reply_markup=keyboards.ReplyKeyboardRemove())


@dp.message_handler(content_types=["contact"], state=States.COURSE)
async def contact_handler_course(message: types.Message, state: FSMContext):
    if not is_banned(message.from_user.id):
        if message.contact is not None:
            username = message.from_user.username
            user_id = message.from_user.id
            contact = message.contact
            insert_user_data_in_db(user_id, contact.phone_number, username)
            await send_to_receiver_from_contact(user_id, username, contact, "Курс")
            update_param_in_db(user_id, "course")
            await bot.send_message(message.from_user.id, "Ваша заявка на курс отправлена📩")
            await state.reset_state()
        else:
            await bot.send_message(message.from_user.id,
                                   "Чтобы записаться вы должны предоставить доступ к номеру телефона")
    else:
        await bot.send_message(message.from_user.id, "Вы забанены🥴")


@dp.message_handler(content_types=["contact"], state=States.CONSULTING)
async def contact_handler_consulting(message: types.Message, state: FSMContext):
    if not is_banned(message.from_user.id):
        if message.contact is not None:
            username = message.from_user.username
            user_id = message.from_user.id
            contact = message.contact
            insert_user_data_in_db(user_id, contact.phone_number, username)
            await send_to_receiver_from_contact(user_id, username, contact, "Консультация")
            update_param_in_db(user_id, "consultation")
            await bot.send_message(message.from_user.id, "Ваша заявка на консультацию отправлена📩")
            await state.reset_state()
        else:
            await bot.send_message(message.from_user.id,
                                   "Чтобы записаться вы должны предоставить доступ к номеру телефона")
    else:
        await bot.send_message(message.from_user.id, "Вы забанены🥴")


@dp.message_handler(content_types=["contact"], state=States.MAP)
async def contact_handler_map(message: types.Message, state: FSMContext):
    if not is_banned(message.from_user.id):
        if message.contact is not None:
            username = message.from_user.username
            user_id = message.from_user.id
            contact = message.contact
            insert_user_data_in_db(user_id, contact.phone_number, username)
            await send_to_receiver_from_contact(user_id, username, contact, "Натальная карта")
            update_param_in_db(user_id, "astro_map")
            await bot.send_message(message.from_user.id, "Ваш запрос на составление натальной карты отправлен📩")
            await state.reset_state()
        else:
            await bot.send_message(message.from_user.id,
                                   "Чтобы записаться вы должны предоставить доступ к номеру телефона")
    else:
        await bot.send_message(message.from_user.id, "Вы забанены🥴")


@dp.message_handler(content_types=["contact"])
async def contact_handler(message: types.Message, state: FSMContext):
    if not is_banned(message.from_user.id):
        if message.contact is not None:
            username = message.from_user.username
            user_id = message.from_user.id
            contact = message.contact
            insert_user_data_in_db(user_id, contact.phone_number, username)
            if request_controller(user_id, "course"):
                await send_to_receiver_from_contact(user_id, username, contact, "Курс")
                update_param_in_db(user_id, "course")
                await bot.send_message(message.from_user.id, "Ваша заявка на курс отправлена📩")
                await state.reset_state()
            else:
                await bot.send_message(user_id, "Вы уже отправили заявку на курс📥")
        else:
            await bot.send_message(message.from_user.id,
                                   "Чтобы записаться вы должны предоставить доступ к номеру телефона")
    else:
        await bot.send_message(message.from_user.id, "Вы забанены🥴")


@dp.message_handler(state=States.COURSE)
async def simple_message_handler_course(message: types.Message, state: FSMContext):
    if message.text == "Другие услуги📝":
        await bot.send_message(message.from_user.id, "Список всех услуг📝", reply_markup=keyboards.services_keyboard)
        await state.reset_state()


@dp.message_handler(state=States.MAP)
async def simple_message_handler_course(message: types.Message, state: FSMContext):
    if message.text == "Другие услуги📝":
        await bot.send_message(message.from_user.id, "Список всех услуг📝", reply_markup=keyboards.services_keyboard)
        await state.reset_state()


@dp.message_handler(state=States.CONSULTING)
async def simple_message_handler_course(message: types.Message, state: FSMContext):
    if message.text == "Другие услуги📝":
        await bot.send_message(message.from_user.id, "Список всех услуг📝", reply_markup=keyboards.services_keyboard)
        await state.reset_state()


@dp.message_handler()
async def simple_message_handler(message: types.Message, state: FSMContext):
    text = message.text
    user_id = message.from_user.id
    if not is_banned(user_id):
        if text == "Другие услуги📝":
            await bot.send_message(user_id, "Список всех услуг📝", reply_markup=keyboards.services_keyboard)
            await state.reset_state()
        elif text == "Записаться на консультацию✏":
            if request_controller(user_id, "consultation"):
                if has_contact(user_id):
                    await send_to_receiver_from_db(user_id, "Консультация")
                    update_param_in_db(user_id, "consultation")
                    await bot.send_message(user_id, "Ваша заявка на консультацию отправлена📩")
                else:
                    await bot.send_message(user_id,
                                           "Чтобы записаться вы должны предоставить доступ к номеру телефона☎",
                                           reply_markup=keyboards.sign_up_reply_keyboard)
                    await States.CONSULTING.set()
            else:
                await bot.send_message(user_id, "Вы уже отправили заявку на консультацию📥")
        elif text == "Записаться на курс📌":
            if request_controller(user_id, "course"):
                if has_contact(user_id):
                    await send_to_receiver_from_db(user_id, "Курс")
                    update_param_in_db(user_id, "course")
                    await bot.send_message(user_id, "Ваша заявка на курс отправлена📩")
                else:
                    await bot.send_message(user_id,
                                           "Чтобы записаться вы должны предоставить доступ к номеру телефона☎",
                                           reply_markup=keyboards.sign_up_reply_keyboard)
                    await States.COURSE.set()
            else:
                await bot.send_message(user_id, "Вы уже отправили заявку на курс📥")
        elif text == "Заказать натальную карту🔮":
            if request_controller(user_id, "astro_map"):
                if has_contact(user_id):
                    await send_to_receiver_from_db(user_id, "Натальная карта")
                    update_param_in_db(user_id, "astro_map")
                    await bot.send_message(user_id, "Ваш запрос на составление натальной карты отправлен📩")
                else:
                    await bot.send_message(user_id,
                                           "Чтобы записаться вы должны предоставить доступ к номеру телефона☎",
                                           reply_markup=keyboards.sign_up_reply_keyboard)
                    await States.MAP.set()
            else:
                await bot.send_message(user_id, "Вы уже отправили запрос на составление натальной карты📥")
    else:
        await bot.send_message(user_id, "Вы забанены🥴")


if __name__ == '__main__':
    executor.start_polling(dp)
