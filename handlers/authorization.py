from os import remove

from emoji import emojize
import logging

from octodiary.asyncApi.myschool import AsyncWebAPI
from octodiary.exceptions import APIError
from octodiary.types.captcha import Captcha

from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.payload import decode_payload

from database.invites import invites
from database.login_tries import login_tries
from database.used_gosuslugi import used_gosuslugi
from database.users import users
from HASH import get_hash

from keyboards.questions import select_stage, select_role
from keyboards.authorization import select_auth_type, cancel

router = Router()


class AuthStates(StatesGroup):
    login_entering = State()
    password_entering = State()

    captcha_text_entering = State()
    captcha_photo_entering = State()
    totp_entering = State()

    manual_code_entering = State()


""" Authorization functions (must be removed)"""


async def handle_captcha(message: Message, state: FSMContext, data, captcha: Captcha, bot: Bot):
    if captcha.question:
        await message.answer(f"Введите ответ на вопрос: \n{str(captcha.question)}")
        data['response'] = captcha
        await state.set_state(AuthStates.captcha_text_entering)
        await state.set_data(data)
    else:
        with open(f"captchas/captcha_{message.chat.id}.png", "wb") as image:
            image.write(captcha.image_bytes)
        photo = FSInputFile(f"captchas/captcha_{message.chat.id}.png")
        await message.answer("Решите капчу:")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
        data['response'] = captcha
        await state.set_state(AuthStates.captcha_photo_entering)
        await state.set_data(data)


async def check_captcha_response(message: Message, state: FSMContext, data, response):
    api = data['api']
    if isinstance(response, bool):
        await message.answer("Введите код из SMS/TOTP приложения(например, Google аутентификатор)")
        await state.set_state(AuthStates.totp_entering)
        await state.set_data(data)
    else:
        data['token'] = response
        api.token = data['token']
        await check_living(message, api)


async def check_living(message: Message, api: AsyncWebAPI):
    res = await api.get_session_info()
    await message.answer("Токен получен.")
    if res.regional_auth == "msk":
        person_id = res.person_id
        if used_gosuslugi.check_existing(used_gosuslugi.hash_person_id(person_id)):
            await message.answer("Ошибка! Пользователь с данной учётной записью уже зарегестрирован.")
            return
        used_gosuslugi.add_hash(person_id)
        await message.answer("Поздравляю, авторизация прошла успешна")
        await message.answer(
            "Выбери свое направление",
            reply_markup=select_role()
        )
    else:
        await message.answer("Ошибка! Судя по всему, вы или не учитесь в МО, или не учитесь в принципе. "
                             "Попробуйте снова, или выберите другой способ авторизации")


@router.message(Command("start"))
async def start(message: Message, command: CommandObject):
    await message.answer(
        emojize(":red_heart:Привет! \n\nЯ - бот, созданный для помощи тебе к подготовке к этапам по технологии"),
    )
    if users.check_existing(message.chat.id):
        await message.answer(
            "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
            "клавиатурой для выбора материалов.", reply_markup=select_stage()
        )
        if users.is_teacher(message.chat.id):
            await message.answer(
                "Пользуясь полномочиями учителя, вы можете загружать материалы при помощи команды /post_material\n"
                "А также, вы можете приглашать учеников с помощью /invite"
            )
        if users.is_admin(message.chat.id):
            await message.answer(
                "Пользуясь полномочиями администратора, вы можете выполнять различные шалости. См. /admin"
            )
    else:
        if command.args is None:
            await message.answer(
                "Данный бот работает только для олимпиадников из Московской области :(\nДля подтверждения вы можете "
                "использовать вход через Госуслуги или через ссылку от преподавателя", reply_markup=select_auth_type()
            )
        else:
            if login_tries.get_tries(message.chat.id) < 3:
                code = decode_payload(command.args)
                if invites.check_existing(code):
                    invites.remove_invite(code)
                    await message.answer("Выберите направление:", reply_markup=select_role())
                else:
                    login_tries.add_try(message.chat.id)
                    await message.answer("Ссылка неверная! Попробуйте снова.")
            else:
                await message.answer("Ссылка неверная! Попробуйте снова.")


@router.message(Command("change_olymp"))
async def change_olymp(message: Message):
    if users.check_existing(message.chat.id):
        await message.answer(
            "Выбери свое направление",
            reply_markup=select_role()
        )


""" Gosuslugi authorization """


@router.callback_query(StateFilter(None), F.data == "auth_gosuslugi")
async def mamont_auth(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Данные для авторизации не сохраняются, используется лишь токен для получения места "
                                  "учебы.\nПосле завершения авторизации вам не придётся каждый раз вводить свои "
                                  f"данные.\nПроект имеет открытый исходный код - {get_hash()}")
    await state.clear()
    await callback.message.answer(
        "Пожалуйста, введите свой логин для авторизации на Госуслугах:",
        reply_markup=cancel()
    )
    await callback.answer()
    await state.set_state(AuthStates.login_entering)


@router.message(AuthStates.login_entering)
async def login_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data['login'] = message.text
    await state.clear()
    await message.answer(
        "Введите свой пароль для авторизации на Госуслугах:",
        reply_markup=cancel()
    )
    await state.set_state(AuthStates.password_entering)
    await state.set_data(data)


@router.message(AuthStates.password_entering)
async def password_entered(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    data['password'] = message.text
    api = data['api'] = AsyncWebAPI()
    await message.answer(
        "Пытаюсь авторизоваться..."
    )
    try:
        response: bool | Captcha = await api.esia_login(data['login'], data['password'])
        if isinstance(response, bool):
            await state.clear()
            await state.set_state(AuthStates.totp_entering)
            await message.answer("Введите код из SMS/TOTP приложения(например, Google аутентификатор)")
            data['response'] = response
            await state.set_data(data)
        else:
            await handle_captcha(message, state, data, response, bot)
    except APIError as e:
        await message.answer("Возникла ошибка в API: ", str(e))
        logging.error(f"Возникла ошибка в API\n{message.chat.id}, {e}")
    except Exception as e:
        logging.error("Непредвиденная ошибка в API password_entered: ", str(e))


@router.message(AuthStates.totp_entering)
async def totp_entered(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    api = data['api']
    await state.clear()
    data['totp'] = message.text.strip()
    try:
        response2 = await api.esia_enter_mfa(code=data['totp'])
        if isinstance(response2, str):
            data['token'] = response2
            api.token = data['token']
            await check_living(message, api)
        else:
            await handle_captcha(message, state, data, response2, bot)

    except APIError as e:
        await message.answer("Возникла ошибка в API: ", str(e))
        logging.error(f"Возникла ошибка в API\n{message.chat.id}, {e}")
    except Exception as e:
        logging.error("Непредвиденная ошибка в API totp_entered: ", str(e))


@router.message(AuthStates.captcha_text_entering)
async def handle_text_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    try:
        response = await data['response'].async_asnwer_captcha(message.text)
        await check_captcha_response(message, state, data, response)
    except APIError:
        await message.answer("Неверный ответ!")


@router.message(AuthStates.captcha_photo_entering)
async def handle_photo_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    response = await data['response'].async_verify_captcha(message.text)
    remove(f"captchas/captcha_{message.chat.id}.png")
    await check_captcha_response(message, state, data, response)


@router.callback_query(F.data.startswith("role_"))
async def query(callback: types.CallbackQuery, command: CommandObject = CommandObject):
    role = callback.data.split('_')[1]
    if users.check_existing(callback.message.chat.id):
        users.change_role(callback.message.chat.id, role)
    users.add_user(callback.message.chat.id, callback.message.chat.username, role)
    await callback.message.delete()
    await start(callback.message, command)


""" Manual authorization """


@router.callback_query(StateFilter(None), F.data == "auth_manual")
async def auth_manual(callback: types.CallbackQuery):
    await callback.message.answer(
        "Попросите вашего преподавателя сгенерировать пригласительную ссылку, и перейдите по ней")
    await callback.answer()
