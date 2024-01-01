from os import remove
from emoji import emojize

from octodiary.asyncApi.myschool import AsyncWebAPI
from octodiary.exceptions import APIError
from octodiary.types.captcha import Captcha

from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database.commands import is_teacher, is_admin, check_existing, add_user

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


async def handle_captcha(message: Message, state: FSMContext, data, captcha: Captcha, bot: Bot):
    if captcha.question:
        await message.answer(f"Введите ответ на вопрос: \n{str(captcha.question)}")
        data['response'] = captcha
        await state.set_state(AuthStates.captcha_text_entering)
        await state.set_data(data)
    else:
        with open(f"captcha_{message.chat.id}.png", "wb") as image:
            image.write(captcha.image_bytes)
        photo = FSInputFile(f"captcha_{message.chat.id}.png")
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
        await message.answer("Поздравляю, авторизация прошла успешна")
        await message.answer(
            "Выбери свое направление",
            reply_markup=select_role()
        )
    else:
        await message.answer("Ошибка! Судя по всему, вы или не учитесь в МО, или не учитесь в принципе. "
                             "Попробуйте снова, или выберите другой способ авторизации")


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        emojize(":red_heart:Привет! \n\nЯ - бот, созданный для помощи тебе к подготовке к этапам по технологии"),
    )
    if check_existing(message.chat.id):
        await message.answer(
            "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
            "клавиатурой для выбора материалов.", reply_markup=select_stage()
        )
        if is_teacher(message.chat.id):
            await message.answer(
                "Пользуясь полномочиями учителя, вы можете загружать материалы при помощи команды /post_material"
            )
        if is_admin(message.chat.id):
            await message.answer(
                "Пользуясь полномочиями администратора, вы можете выполнять различные шалости. См. /admin"
            )
    else:
        await message.answer(
            "Данный бот работает только для олимпиадников из Московской области :(\nДля подтверждения вы можете "
            "использовать вход через Госуслуги или ручное подтверждение от учителя(скорость зависит от реакции "
            "преподавателя)", reply_markup=select_auth_type()
        )


@router.callback_query(StateFilter(None), F.data == "auth_gosuslugi")
async def mamont_auth(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Пожалуйста, введите свой логин для авторизации на Госуслугах.\n\nДанные об авторизации у нас не "
        "сохраняются.\nПроект имеет открытый исходный код - https://github.com/Uknown-creator/techno_vsosh",
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
        "Введите свой пароль для авторизации на Госуслугах.\n\nДанные об авторизации у нас не "
        "сохраняются.\nПроект имеет открытый исходный код - https://github.com/Uknown-creator/techno_vsosh",
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


@router.message(AuthStates.captcha_text_entering)
async def handle_text_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    response = await data['response'].async_asnwer_captcha(message.text)
    await check_captcha_response(message, state, data, response)


@router.message(AuthStates.captcha_photo_entering)
async def handle_photo_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    response = await data['response'].async_verify_captcha(message.text)
    remove(f"captcha_{message.chat.id}.png")
    await check_captcha_response(message, state, data, response)


@router.callback_query(F.data.startswith("role_"))
async def query(callback: types.CallbackQuery):
    role = callback.data.split('_')[1]
    add_user(callback.message.chat.id, callback.message.chat.username, role)
    await callback.message.delete()
    await callback.message.answer(
        "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
        "клавиатурой для выбора материалов", reply_markup=select_stage()
    )
    await callback.answer()
