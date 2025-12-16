from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State

from database.users import users
from database.materials import materials
from keyboards.materials import select_header, select_year

from emoji import emojize

router = Router()


class MaterialSelecting(StatesGroup):
    type_selected = State()
    header_selected = State()


@router.callback_query(F.data == "cancel")
async def cal_cancel(callback: types.CallbackQuery, state: FSMContext):
    """
    Docstring for cal_cancel
    
    :param callback: Description
    :type callback: types.CallbackQuery
    :param state: Description
    :type state: FSMContext
    """
    await state.clear()
    await callback.message.answer("Команда отменена.")
    await callback.answer()
    await callback.message.delete()


@router.message(F.text.lower() == "теория")
async def theory(message: Message, state: FSMContext):
    """
    Docstring for theory
    
    :param message: Description
    :type message: Message
    :param state: Description
    :type state: FSMContext
    """
    if users.check_existing(message.chat.id):
        olymp = users.get_role(message.chat.id)
        await message.answer(
            emojize("Выбери нужный тебе материал:\n:frog:"),
            reply_markup=select_header(olymp, 0)
        )
        await state.set_state(MaterialSelecting.type_selected)
        await state.update_data(olymp=olymp, direction=0)


@router.message(F.text.lower() == "практика")
async def practice(message: Message, state: FSMContext):
    """
    Docstring for practice
    
    :param message: Description
    :type message: Message
    :param state: Description
    :type state: FSMContext
    """
    if users.check_existing(message.chat.id):
        olymp = users.get_role(message.chat.id)
        await message.answer(
            emojize("Выбери нужный тебе материал:\n:frog:"),
            reply_markup=select_header(olymp, 1)
        )
        await state.set_state(MaterialSelecting.type_selected)
        await state.update_data(olymp=olymp, direction=1)


@router.message(F.text.lower() == "проект")
async def practice(message: Message, state: FSMContext):
    """
    Docstring for practice
    
    :param message: Description
    :type message: Message
    :param state: Description
    :type state: FSMContext
    """
    if users.check_existing(message.chat.id):
        olymp = users.get_role(message.chat.id)
        await message.answer(
            emojize("Выбери нужный тебе материал:\n:frog:"),
            reply_markup=select_header(olymp, 2)
        )
        await state.set_state(MaterialSelecting.type_selected)
        await state.update_data(olymp=olymp, direction=2)


@router.callback_query(F.data.startswith('header_'), MaterialSelecting.type_selected)
async def years(callback: types.CallbackQuery, state: FSMContext):
    """
    Docstring for years
    
    :param callback: Description
    :type callback: types.CallbackQuery
    :param state: Description
    :type state: FSMContext
    """
    data = await state.get_data()
    olymp = int(data['olymp'])
    direction = int(data['direction'])
    header = callback.data.split('_')[1]
    await callback.message.edit_reply_markup(reply_markup=select_year(olymp, direction, header))
    await callback.answer()
    await state.clear()
    await state.set_state(MaterialSelecting.header_selected)
    await state.update_data(olymp=olymp, direction=direction, header=header)


@router.callback_query(F.data.startswith('year_'), MaterialSelecting.header_selected)
async def get_materials(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """
    Docstring for get_materials
    
    :param callback: Description
    :type callback: types.CallbackQuery
    :param bot: Description
    :type bot: Bot
    :param state: Description
    :type state: FSMContext
    """
    data = await state.get_data()
    year = int(callback.data.split('_')[1])
    material = materials.get_material(data['olymp'], data['direction'], data['header'], year)
    if material.startswith("file_"):
        file = '_'.join(i for i in material.split('_')[1:])
        await bot.send_document(callback.message.chat.id, file)
    else:
        await callback.message.answer(material)
    await callback.answer()
    await state.clear()
