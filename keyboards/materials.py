from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
import emoji
from database.commands import get_types, get_headers, get_materials


def select_header(user_id: int, direction: int, type_of_material: str = None):
    builder = InlineKeyboardBuilder()
    if type_of_material is None:
        for header_type in get_types(user_id, direction):
            builder.add(types.InlineKeyboardButton(
                text=f"{header_type[0]}",
                callback_data=f"types_{user_id}_{direction}_{header_type[0]}"
            ))
        builder.adjust(1)
        return builder.as_markup()
    else:
        for header in get_headers(user_id, direction, type_of_material):
            builder.add(types.InlineKeyboardButton(
                text=f"{header[0]}",  # IF commands.get_materials only with header will be broken
                callback_data=f"header_{header[0]}"  # {user_id}_{direction}_{type_of_material}
            ))
        builder.adjust(1)
        return builder.as_markup()
