from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.users import is_admin, is_teacher
from database.materials import post_materials, get_materials_by_userid
from keyboards.authorization import cancel
from keyboards.materials import select_olymp, select_stage, select_type, select_type_of_material

from time import strftime

router = Router()


class MaterialStates(StatesGroup):
    types_receive = State()
    headers_receive = State()
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
        "Напиши тип материала(задания/ответы/пз)\nИли выберите из текущих:",  # Проверка на длину!!!
        reply_markup=select_type(olymp, stage))
    await state.set_state(MaterialStates.types_receive)
    data = await state.get_data()
    data['olymp'] = olymp
    data['stage'] = stage
    await state.set_data(data)


@router.callback_query(F.data.startswith('type_'))
async def chosen_type(callback: types.CallbackQuery, state: FSMContext):
    callback_data = callback.data.split('_')
    data = await state.get_data()
    await state.clear()
    await callback.answer()
    await callback.message.answer("Отлично, теперь введите название заголовка для материала:\nПостарайтесь сделать "
                                  "уникальный заголовок для материала, включая в него направление/год/т.п.")
    await state.set_state(MaterialStates.headers_receive)
    data['olymp'] = callback_data[1]
    data['stage'] = callback_data[2]
    data['header_type'] = callback_data[3]
    await state.set_data(data)


@router.message(MaterialStates.types_receive)
async def printing_type(message: Message, state: FSMContext):
    if len(f"types_{message.text}".encode('utf-8')) > 64:
        await message.answer("Пожалуйста, уменьшите текст! Команда отменена")
        await state.clear()
        return
    data = await state.get_data()
    data['header_type'] = message.text
    await state.clear()
    await message.answer("Отлично, теперь введите название заголовка для материала:\nПостарайтесь сделать "
                         "уникальный заголовок для материала, включая в него направление/год/т.п.")
    await state.set_state(MaterialStates.headers_receive)
    await state.set_data(data)


@router.message(MaterialStates.headers_receive)
async def headers_received(message: Message, state: FSMContext):  # Проверка на null строку/некорректный ввод
    if len(f"header_{message.text}".encode('utf-8')) > 64:
        await message.answer("Пожалуйста, уменьшите текст! Команда отменена")
        await state.clear()
        return
    data = await state.get_data()
    data['header'] = message.text
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
    stage = data['stage']
    header_type = data['header_type']
    header = data['header']
    material = message.text
    await state.clear()
    try:
        time_created = strftime("%H:%M:%S %d-%m-%Y")
        post_materials(message.chat.id, time_created, olymp, stage, header_type, header, material)
        await message.answer("Задания загрузились!")
    except Exception as e:
        await message.answer(
            f"Ошибка!\n {e}"
        )


@router.message(MaterialStates.material_document_receive)
async def material_file_received(message: Message, state: FSMContext):
    data = await state.get_data()
    olymp = data['olymp']
    stage = data['stage']
    header_type = data['header_type']
    header = data['header']
    await state.clear()
    try:
        file_id = message.document.file_id
        time_created = strftime("%H:%M:%S %d-%m-%Y")
        post_materials(message.chat.id, time_created, olymp, stage, header_type, header, f"file_{file_id}")
        await message.answer("Задания загрузились!")
    except Exception as e:
        await message.answer(f"Ошибка!\n{e}")


@router.message(Command('show_materials'))
async def show_materials(message: Message):
    if is_teacher(message.chat.id) or is_admin(message.chat.id):
        await message.answer(get_materials_by_userid(message.chat.id))
