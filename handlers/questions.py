from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.methods.send_animation import SendAnimation
from aiogram import methods
from database import commands
from keyboards.questions import select_role, select_stage
import emoji

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        emoji.emojize(":red_heart:Привет! \n\nЯ - бот, созданный для помощи тебе к подготовке к этапам по технологии"),
    )
    if commands.check_existing(message.chat.id):
        roles = commands.get_roles(message.chat.id)[0]
        await message.answer(
            "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
            "клавиатурой для выбора материалов", reply_markup=select_stage()
        )
        if roles[0] == 1:
            await message.answer(
                "Приветствую, администратор!\n\n/post_news - Запостить жабу\n/add_admin - Добавить "
                "жабу\n/delete_admin - Удалить жабу\n/check_log - Смотрим на жаб\n/return_users - Вывод "
                "жабобят\n/return_admins - Вывод жаб\n/edit_user - редактор жаб\n\nБот работает"
            )
    else:
        await message.answer(
            "Выбери свое направление",
            reply_markup=select_role()
        )


@router.callback_query(F.data.startswith("role_"))
async def query(callback: types.CallbackQuery):
    role = callback.data.split('_')[1]
    commands.add_user(callback.message.chat.id, callback.message.chat.username, role)
    await callback.message.delete()
    await callback.message.answer(
        "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
        "клавиатурой для выбора материалов", reply_markup=select_stage()
    )
    await callback.answer(
        text="",
        show_alert=True
    )


@router.message(F.text.lower() == "теория")
async def materials(message: Message):
    await message.answer(emoji.emojize("Держи жабу\n:frog:"))
    # await message.answer(f"А я знаю, что ты {commands.convert_role(commands.get_roles(message.chat.id)[0][1])}")
    # await SendAnimation
