from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import emoji


def select_role():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=emoji.emojize(":desktop_computer:Я ИБшник"),
        callback_data="role_ib"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emoji.emojize(":hammer_and_wrench:Я ТТшник"),
        callback_data="role_tt"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emoji.emojize(":sewing_needle:Я КДшник"),
        callback_data="role_kd"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emoji.emojize(":alien_monster:Я РТшник"),
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

