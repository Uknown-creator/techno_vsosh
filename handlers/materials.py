from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from database.commands import get_materials, get_role, is_admin, is_teacher, post_materials
from keyboards.materials import select_olymp, select_stage, select_type, select_header_by_user
from emoji import emojize

router = Router()


class MaterialStates(StatesGroup):
    types_receive = State()
    headers_receive = State()
    material_receive = State()


# TODO: cancelling selecting materials when its empty
@router.message(F.text.lower() == "теория")
async def theory(message: Message):
    olymp = get_role(message.chat.id)[0][0]
    await message.answer(
        emojize("Выбери нужный тебе материал:\n:frog:"),
        reply_markup=select_header_by_user(olymp, 0)
    )


@router.message(F.text.lower() == "практика")
async def practice(message: Message):
    olymp = get_role(message.chat.id)[0][0]
    await message.answer(
        emojize("Выбери нужный тебе материал:\n:frog:"),
        reply_markup=select_header_by_user(olymp, 1)
    )


@router.message(F.text.lower() == "проект")
async def practice(message: Message):
    olymp = get_role(message.chat.id)[0][0]
    await message.answer(
        emojize("Выбери нужный тебе материал:\n:frog:"),
        reply_markup=select_header_by_user(olymp, 2)
    )


@router.callback_query(F.data.startswith('types_'))  # theory, practice and project
async def headers(callback: types.CallbackQuery):
    data = callback.data.split('_')[1:]
    olymp = int(data[0])
    direction = int(data[1])
    header = data[2]
    await callback.message.edit_reply_markup(reply_markup=select_header_by_user(olymp, direction, header))


@router.callback_query(F.data.startswith('header_'))
async def materials(callback: types.CallbackQuery):
    data = callback.data.split('_')[1:]
    header = data[0]
    await callback.message.answer(str(get_materials(header)[0][0]))
    await callback.answer()


@router.message(Command('post_material'))
async def post_material(message: Message):
    if is_teacher(message.chat.id) or is_admin(message.chat.id):
        await message.answer(
            "Выбери:\nНаправление олимпиады,\nЭтап(теория/практика/проект)\n\nИспользуй клавиатуру снизу сообщения:",
            reply_markup=select_olymp()
        )


@router.callback_query(F.data.startswith('olymp_'))
async def selecting_stage(callback: types.CallbackQuery):
    olymp = int(callback.data.split('_')[1])
    await callback.message.edit_reply_markup(reply_markup=select_stage(olymp))


@router.callback_query(StateFilter(None), F.data.startswith('stage_'))
async def selecting_type(callback: types.CallbackQuery, state: FSMContext):
    olymp, stage = int(callback.data.split('_')[1]), int(callback.data.split('_')[2])
    await callback.answer()
    await callback.message.answer(
        "Напиши тип материала(задания/ответы/пз)\nИли выберите из текущих:",
        reply_markup=select_type(olymp, stage))
    await state.set_state(MaterialStates.types_receive)
    data = await state.get_data()
    data['olymp'] = olymp
    data['stage'] = stage
    await state.set_data(data)


@router.callback_query(F.data.startswith('type_'))
async def chosen_type(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split('_')[1]
    olymp = callback_data[0]
    stage = callback_data[1]
    type_of_header = callback_data[2]
    await state.clear()
    await callback.message.answer("Отлично, теперь введите название заголовка для материала:")
    await state.set_state(MaterialStates.headers_receive)
    data = await state.get_data()
    data['olymp'] = olymp
    data['stage'] = stage
    data['type_of_header'] = type_of_header
    await state.set_data(data)


@router.message(MaterialStates.types_receive)
async def printing_type(message: Message, state: FSMContext):
    data = await state.get_data()
    data['olymp'] = data['olymp']
    data['stage'] = data['stage']  # Absolutely no-reasonable equal, it was made for test
    data['type_of_header'] = message.text
    await state.clear()
    await message.answer("Отлично, теперь введите название заголовка для материала:")
    await state.set_state(MaterialStates.headers_receive)
    await state.set_data(data)


@router.message(MaterialStates.headers_receive)
async def headers_received(message: Message, state: FSMContext):
    data = await state.get_data()
    data['header'] = message.text
    await state.clear()
    await message.answer(
        "Остался последний штрих: загрузить сам материал\n\nК сожалению, пока это можно оформить только в виде "
        "текста. Загрузка фото/видео и документов появится позже"
    )
    await state.set_state(MaterialStates.material_receive)
    await state.set_data(data)


@router.message(MaterialStates.material_receive)
async def text_received(message: Message, state: FSMContext):
    data = await state.get_data()
    olymp = data['olymp']
    stage = data['stage']
    type_of_header = data['type_of_header']
    header = data['header']
    material = message.text
    await state.clear()
    try:
        post_materials(olymp, stage, type_of_header, header, material)
        await message.answer("Задания загрузились!")
    except Exception as e:
        await message.answer(
            f"Ошибка!\n {e}"
        )
