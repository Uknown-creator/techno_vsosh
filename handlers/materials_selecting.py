from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State

from database.users import get_role, check_existing
from database.materials import get_materials_by_header
from keyboards.materials import select_header_by_user

from emoji import emojize

router = Router()


class MaterialSelecting(StatesGroup):
    type_selected = State()
    header_selected = State()


@router.callback_query(F.data == "cancel")
async def cal_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Команда отменена.")
    await callback.answer()
    await callback.message.delete()


@router.message(F.text.lower() == "теория")
async def theory(message: Message, state: FSMContext):
    if check_existing(message.chat.id):
        olymp = get_role(message.chat.id)
        print(olymp)
        await message.answer(
            emojize("Выбери нужный тебе материал:\n:frog:"),
            reply_markup=select_header_by_user(olymp, 0)
        )
        await state.set_state(MaterialSelecting.type_selected)
        await state.update_data(olymp=olymp, direction=0)


@router.message(F.text.lower() == "практика")
async def practice(message: Message, state: FSMContext):
    if check_existing(message.chat.id):
        olymp = get_role(message.chat.id)
        await message.answer(
            emojize("Выбери нужный тебе материал:\n:frog:"),
            reply_markup=select_header_by_user(olymp, 1)
        )
        await state.set_state(MaterialSelecting.type_selected)
        await state.update_data(olymp=olymp, direction=1)


@router.message(F.text.lower() == "проект")
async def practice(message: Message, state: FSMContext):
    if check_existing(message.chat.id):
        olymp = get_role(message.chat.id)
        await message.answer(
            emojize("Выбери нужный тебе материал:\n:frog:"),
            reply_markup=select_header_by_user(olymp, 2)
        )
        await state.set_state(MaterialSelecting.type_selected)
        await state.update_data(olymp=olymp, direction=2)


@router.callback_query(F.data.startswith('types_'), MaterialSelecting.type_selected)
async def headers(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    olymp = int(data['olymp'])
    direction = int(data['direction'])
    header = callback.data.split('_')[1]
    await callback.message.edit_reply_markup(reply_markup=select_header_by_user(olymp, direction, header))
    await callback.answer()
    await state.clear()
    await state.set_state(MaterialSelecting.header_selected)


@router.callback_query(F.data.startswith('header_'), MaterialSelecting.header_selected)
async def materials(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """ May not work if headers on different olympiads are same"""
    header = callback.data.split('_')[1]
    material = get_materials_by_header(header)
    if material.startswith("file_"):
        file = '_'.join(i for i in material.split('_')[1:])
        await bot.send_document(callback.message.chat.id, file)
    else:
        await callback.message.answer(get_materials_by_header(header))
    await callback.answer()
    await state.clear()
