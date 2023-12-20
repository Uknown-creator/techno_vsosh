from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
from database import commands
from database.commands import is_teacher, is_admin
from keyboards.questions import select_role, select_stage
import emoji

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        emoji.emojize(":red_heart:Привет! \n\nЯ - бот, созданный для помощи тебе к подготовке к этапам по технологии"),
    )
    if commands.check_existing(message.chat.id):
        # roles = commands.get_role(message.chat.id)
        await message.answer(
            "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
            "клавиатурой для выбора материалов.\nЕсли понадобится её скрыть, введите /hide", reply_markup=select_stage()
        )
        if is_teacher(message.chat.id):
            await message.answer(
                "Пользуясь полномочиями учителя, вы можете загружать материалы при помощи команды /post_material"
            )
        elif is_admin(message.chat.id):
            await message.answer(
                "Пользуясь полномочиями администратора, вы можете выполнять различные шалости. См. /admin"
            )
    else:
        # auth

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
    await callback.answer()
