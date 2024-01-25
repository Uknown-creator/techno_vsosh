from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.users import users
from database.materials import materials
from keyboards.authorization import cancel
from keyboards.materials import select_olymp, select_type, select_year, select_type_of_material, select_header

from time import strftime

router = Router()


class MaterialStates(StatesGroup):
    headers_receive = State()
    years_receive = State()
    material_text_receive = State()
    material_document_receive = State()


@router.callback_query(F.data == "cancel")
async def cal_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Команда отменена.")
    await callback.answer()
    await callback.message.delete()


@router.message(Command('post_material'))
async def post_material(message: Message):
    if users.is_teacher(message.chat.id) or users.is_admin(message.chat.id):
        await message.answer(
            "Выбери:\nНаправление олимпиады,\nЭтап(теория/практика/проект)\n\nИспользуй клавиатуру снизу сообщения:",
            reply_markup=select_olymp()
        )


@router.callback_query(F.data.startswith('olymp_'))
async def callback_olymp_received(callback: types.CallbackQuery):
    olymp = int(callback.data.split('_')[1])
    await callback.message.edit_reply_markup(reply_markup=select_type(olymp))


@router.callback_query(StateFilter(None), F.data.startswith('type_'))
async def callback_type_received(callback: types.CallbackQuery, state: FSMContext):
    olymp, material_type = int(callback.data.split('_')[1]), int(callback.data.split('_')[2])
    await callback.message.answer(
        "Напиши название для материала(задания/ответы/пз)\nИли выбери из текущих:",
        reply_markup=select_header(olymp, material_type))
    await state.clear()
    await state.set_state(MaterialStates.headers_receive)
    await state.update_data(olymp=olymp, material_type=material_type)
    await callback.answer()


@router.callback_query(F.data.startswith('header_'))
async def callback_header_received(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split('_')
    data = await state.get_data()
    data['header'] = callback_data[1]
    await state.clear()
    await callback.message.answer("Введите год олимпиады(одно число) или выберите из предложенных "
                                  "\nЕсли олимпиада 2022-2023, введите 2023",
                                  reply_markup=select_year(data['olymp'], data['material_type'], data['header']))
    await state.set_state(MaterialStates.years_receive)
    await state.set_data(data)
    await callback.answer()


@router.message(MaterialStates.headers_receive)
async def header_received(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    data['header'] = message.text
    await state.clear()
    await message.answer("Введите год олимпиады(одно число) или выберите из предложенных"
                         "\nЕсли олимпиада 2022-2023, введите 2023")
    await state.set_state(MaterialStates.years_receive)
    await state.set_data(data)


@router.callback_query(F.data.startswith('year_'))
async def callback_years_received(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split('_')
    data = await state.get_data()
    data['year'] = int(callback_data[1])
    await state.clear()
    print(materials.check_existing(data['olymp'], data['material_type'], data['header'], data['year']))
    if materials.check_existing(data['olymp'], data['material_type'], data['header'], data['year']):
        await callback.message.answer("Ошибка! Материал с такими данными уже существует.")
        await callback.answer()
        return
    await callback.message.answer(
        "Остался последний штрих: загрузить сам материал. Выберите тип загружаемого материала:\n\n"
        "Внимание! Если файл весит больше 20 мегабайт, то отправьте ссылку на него через облачное хранилище"
        "(Яндекс диск и пр.)",
        reply_markup=select_type_of_material()
    )
    await state.set_data(data)
    await callback.answer()


@router.message(MaterialStates.years_receive)
async def years_received(message: Message, state: FSMContext):
    data = await state.get_data()
    if not message.text.isdigit():
        await message.answer("Ошибка! Введите только число, без других символов.")
        return
    if materials.check_existing(data['olymp'], data['material_type'], data['header'], data['year']):
        await message.answer("Ошибка! Материал с такими данными уже существует.")
        return
    data['year'] = int(message.text)
    await state.clear()
    await message.answer(
        "Остался последний штрих: загрузить сам материал. Выберите тип загружаемого материала:\n\n"
        "Внимание! Если файл весит больше 20 мегабайт, то отправьте ссылку на него через облачное хранилище"
        "(Яндекс диск и пр.)",
        reply_markup=select_type_of_material()
    )
    await state.set_data(data)


@router.callback_query(F.data.startswith("material_"))
async def type_of_material(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split('_')
    data = await state.get_data()
    await state.clear()
    if callback_data[1] == "text":
        await callback.message.answer("Введите текст:")
        await state.set_state(MaterialStates.material_text_receive)
    else:
        await callback.message.answer("Отправьте файл боту в формате документа(в т.ч. фото)",
                                      reply_markup=cancel())
        await state.set_state(MaterialStates.material_document_receive)
    await state.set_data(data)
    await callback.answer()


@router.message(MaterialStates.material_text_receive)
async def material_text_received(message: Message, state: FSMContext):
    data = await state.get_data()
    olymp = data['olymp']
    material_type = data['material_type']
    header = data['header']
    year = data['year']
    material = message.text
    await state.clear()
    try:
        time_created = strftime("%H:%M:%S %d-%m-%Y")
        materials.post_materials(message.chat.id, time_created, olymp, material_type, header, year, material)
        await message.answer("Задания загрузились!")
    except Exception as e:
        await message.answer(
            f"Ошибка!\n {e}"
        )


@router.message(MaterialStates.material_document_receive)
async def material_file_received(message: Message, state: FSMContext):
    data = await state.get_data()
    olymp = data['olymp']
    material_type = data['material_type']
    header = data['header']
    year = data['year']
    await state.clear()
    try:
        file_id = message.document.file_id
        time_created = strftime("%H:%M:%S %d-%m-%Y")
        materials.post_materials(
            message.chat.id, time_created, olymp, material_type, header, year, f"file_{file_id}"
        )
        await message.answer("Задания загрузились!")
    except Exception as e:
        await message.answer(f"Ошибка!\n{e}")


@router.message(Command('show_materials'))
async def show_materials(message: Message):
    if users.is_teacher(message.chat.id) or users.is_admin(message.chat.id):
        await message.answer(materials.get_materials_by_userid(message.chat.id))
