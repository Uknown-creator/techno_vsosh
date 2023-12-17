from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.methods.send_animation import SendAnimation

from database import commands
from keyboards.questions import select_role, select_stage
import emoji

router = Router()


# TODO: adding admins, editing users, posting news

@router.message(Command('return_users'))
async def users(message: Message):
    if commands.get_roles(message.chat.id)[0][0] == 1:
        res = ''
        for user in commands.get_users():
            if user[1]:
                res += f"@{user[1]} - "
            else:
                res += f"ID: {user[0]} - "
            if user[2] == 0:
                res += "user, "
            else:
                res += "admin, "
            res += f"{commands.convert_role(user[-1])}\n"
        await message.answer(res)


@router.message(Command('return_admins'))
async def admins(message: Message):
    if commands.get_roles(message.chat.id)[0][0] == 1:
        await message.answer(str(commands.get_admins()))
