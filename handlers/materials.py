from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.methods.send_animation import SendAnimation
from aiogram import methods
from database.commands import get_materials
from keyboards.materials import select_header
import emoji

router = Router()


# TODO: cancelling selecting materials when its empty
@router.message(F.text.lower() == "теория")
async def theory(message: Message):
    await message.answer(
        emoji.emojize("Выбери нужный тебе материал:\n:frog:"),
        reply_markup=select_header(message.chat.id, 0)
    )


@router.message(F.text.lower() == "практика")
async def practice(message: Message):
    await message.answer(
        emoji.emojize("Выбери нужный тебе материал:\n:frog:"),
        reply_markup=select_header(message.chat.id, 1)
    )


@router.message(F.text.lower() == "проект")
async def practice(message: Message):
    await message.answer(
        emoji.emojize("Выбери нужный тебе материал:\n:frog:"),
        reply_markup=select_header(message.chat.id, 2)
    )


@router.callback_query(F.data.startswith('types_'))  # theory, practice and project
async def headers(callback: types.CallbackQuery):
    data = callback.data.split('_')[1:]
    user_id = int(data[0])
    direction = int(data[1])
    header = data[2]
    await callback.message.edit_reply_markup(reply_markup=select_header(user_id, direction, header))


@router.callback_query(F.data.startswith('header_'))
async def materials(callback: types.CallbackQuery):
    data = callback.data.split('_')[1:]
    header = data[0]
    print(data)
    await callback.message.answer(str(get_materials(header)))
    await callback.answer()
