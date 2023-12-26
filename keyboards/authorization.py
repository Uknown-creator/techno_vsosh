from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize


def cancel():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    return builder.as_markup()


def select_auth_type():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Госуслуги",
        callback_data="auth_gosuslugi"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Ввести код от преподавателя",
        callback_data="auth_manual"
    ))
    builder.adjust(1)
    return builder.as_markup()
