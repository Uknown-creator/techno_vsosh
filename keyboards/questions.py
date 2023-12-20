from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from emoji import emojize


def select_role():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=emojize(":desktop_computer:Я ИБшник"),
        callback_data="role_ib"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":hammer_and_wrench:Я ТТшник"),
        callback_data="role_tt"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":sewing_needle:Я КДшник"),
        callback_data="role_kd"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":alien_monster:Я РТшник"),
        callback_data="role_rt"
    ))
    builder.adjust(2)
    return builder.as_markup()


def select_stage():
    kb = [
        [types.KeyboardButton(text="Теория")],
        [types.KeyboardButton(text="Практика")],
        [types.KeyboardButton(text="Проект")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    return keyboard


def yes_or_no():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=emojize("Да"),
        callback_data="yes"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize("Нет"),
        callback_data="no"
    ))
    builder.adjust(2)
    return builder.as_markup()
