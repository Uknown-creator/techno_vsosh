from octodiary.asyncApi.myschool import AsyncWebAPI
from octodiary.exceptions import APIError
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from octodiary.types.captcha import Captcha

from database import commands
from database.commands import is_teacher, is_admin
from keyboards.questions import select_role, select_stage
from keyboards.authorization import select_auth_type, cancel
import emoji
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()


class AuthStates(StatesGroup):
    login_entering = State()
    password_entering = State()
    captcha_entering = State()
    totp_entering = State()
    manual_code_entering = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        emoji.emojize(":red_heart:Привет! \n\nЯ - бот, созданный для помощи тебе к подготовке к этапам по технологии"),
    )
    if commands.check_existing(message.chat.id):
        # roles = commands.get_role(message.chat.id)
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
    await callback.message.answer(
        "Пожалуйста, введите свой логин для авторизации на Госуслугах.\n\nДанные об авторизации у нас не "
        "сохраняются.\nПроект имеет открытый исходный код - https://github.com/Uknown-creator/techno_vsosh",
        reply_markup=cancel()
    )
    await state.set_state(AuthStates.login_entering)


@router.message(AuthStates.login_entering)
async def login_entered(message: Message, state: FSMContext):
    data = await state.get_data()
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
async def password_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    data['password'] = message.text
    await state.clear()
    await message.answer(
        "Пытаюсь авторизоваться..."
    )
    try:
        response: bool | Captcha = await AsyncWebAPI().esia_login(data['login'], data['password'])
        if isinstance(response, bool):
            await state.set_state(AuthStates.totp_entering)
            await message.edit_text("Введите код из SMS/TOTP приложения")
            data['response'] = response
            await state.set_data(data)
        else:
            pass
            # handle captcha
    except APIError as e:
        await message.answer("Возникла ошибка в API: ", str(e))


@router.message(AuthStates.totp_entering)
async def totp_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    data['totp'] = message.text.strip()
    try:
        response2 = await AsyncWebAPI().esia_enter_mfa(data['totp'])
        if isinstance(response2, str):
            token = response2
            await message.answer("Токен получен.")
        else:
            pass
            # handle captcha
    except APIError as e:
        await message.answer("Возникла ошибка в API: ", str(e))
