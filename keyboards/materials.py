from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.commands import get_headers, get_types
from emoji import emojize


def select_header_by_user(olymp: int, stage: int, type_of_material: str = None):
    builder = InlineKeyboardBuilder()
    if type_of_material is None:
        for header_type in get_types(olymp, stage):
            builder.add(types.InlineKeyboardButton(
                text=f"{header_type[0]}",
                callback_data=f"types_{olymp}_{stage}_{header_type[0]}"
            ))
        builder.add(types.InlineKeyboardButton(
            text=emojize(":cross_mark:Отмена"),
            callback_data="cancel"
        ))
        builder.adjust(1)
        return builder.as_markup()
    else:
        for header in get_headers(olymp, stage, type_of_material):
            builder.add(types.InlineKeyboardButton(
                text=f"{header[0]}",  # IF commands.get_materials only with header will be broken
                callback_data=f"header_{header[0]}"  # {olymp}_{stage}_{type_of_material}
            ))
        builder.add(types.InlineKeyboardButton(
            text=emojize(":cross_mark:Отмена"),
            callback_data="cancel"
        ))
        builder.adjust(1)
        return builder.as_markup()


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


def select_stage(olymp: int):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Теория",
        callback_data=f"stage_{olymp}_0"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Практика",
        callback_data=f"stage_{olymp}_1"
    ))
    builder.add(types.InlineKeyboardButton(
        text="Проект",
        callback_data=f"stage_{olymp}_2"
    ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    return builder.as_markup()


def select_type(olymp: int, stage: int):
    builder = InlineKeyboardBuilder()
    list_of_types = list(set(get_types(olymp, stage)))
    for header_type in list_of_types:
        builder.add(types.InlineKeyboardButton(
            text=f"{header_type[0]}",
            callback_data=f"type_{olymp}_{stage}_{header_type[0]}"
        ))
    builder.add(types.InlineKeyboardButton(
        text=emojize(":cross_mark:Отмена"),
        callback_data="cancel"
    ))
    builder.adjust(1)
    return builder.as_markup()
