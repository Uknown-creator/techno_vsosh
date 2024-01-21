from emoji import emojize

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.materials import materials


def select_olymp():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="ТТиТ",
        callback_data="olymp_0"
    ))
    builder.add(types.InlineKeyboardButton(
        text="ИБ",
        callback_data="olymp_1"
    ))
    builder.add(types.InlineKeyboardButton(
        text="КД",
        callback_data="olymp_2"
    ))
    builder.add(types.InlineKeyboardButton(
        text="РТ",
        callback_data="olymp_3"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel"
    ))
    builder.adjust(1)
    return builder.as_markup()


def select_type(olymp: int):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Теория",
        callback_data=f"type_{olymp}_0"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Практика",
        callback_data=f"type_{olymp}_1"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Проект",
        callback_data=f"type_{olymp}_2"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    return builder.as_markup()


def select_header(olymp: int, material_type: int):
    builder = InlineKeyboardBuilder()
    for header in list(set(materials.get_headers(olymp, material_type))):
        builder.add(types.InlineKeyboardButton(
            text=f"{header}",
            callback_data=f"header_{header}"
        ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    builder.adjust(1)
    return builder.as_markup()


def select_year():
    builder = InlineKeyboardBuilder()
    list_of_types = list(set(materials.get_years()))
    for year in list_of_types:
        builder.add(types.InlineKeyboardButton(
            text=f"{year}",
            callback_data=f"year_{year}"
        ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    builder.adjust(1)
    return builder.as_markup()


def select_type_of_material():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Текст",
        callback_data=f"material_text"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Файл",
        callback_data=f"material_file"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    builder.adjust(1)
    return builder.as_markup()
