from aiogram import Router, F, types, Bot
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.commands import is_admin, add_admin, get_users, convert_role, add_teacher
from keyboards.questions import yes_or_no

router = Router()


class AdminStates(StatesGroup):
    news_receive = State()


@router.message(Command('admin'))
async def admin_commands(message: Message):
    if is_admin(message.chat.id):
        await message.answer(
            "Приветствую, администратор!\n\n/post_material - добавить материал/post_news - Запостить "
            "новость\n/add_admin {id}- Добавить"
            "админа\n/return_users - Вывод пользователей"
            "жабобят\n/logs - Логи\n\nБот работает"
        )


@router.message(Command('add_admin'))
async def add_admin(
        message: Message,
        command: CommandObject
):
    if is_admin(message.chat.id):
        if command.args is None:
            await message.answer(
                "Ошибка! Введите аргумент ID"
            )
            return
        try:
            user_id = int(command.args)
        except ValueError:
            await message.answer(
                "Ошибка: неверно переданы аргументы. Пример:\n/add_admin {ID человека}"
            )
            return
        await add_admin(user_id)
        await message.answer("Готово.")


@router.message(Command('add_teacher'))
async def add_teacher(
        message: Message,
        command: CommandObject
):
    if is_admin(message.chat.id):
        if command.args is None:
            await message.answer(
                "Ошибка! Введите аргумент ID"
            )
            return
        try:
            user_id = int(command.args)
        except ValueError:
            await message.answer(
                "Ошибка: неверно переданы аргументы. Пример:\n/add_teacher {ID человека}"
            )
            return
        await add_teacher(user_id)
        await message.answer("Готово")


@router.message(StateFilter(None), Command('post_news'))
async def broadcast(message: Message, state: FSMContext):
    if is_admin(message.chat.id):
        await message.answer('Отправь новость:')
        await state.set_state(AdminStates.news_receive)


@router.message(AdminStates.news_receive)
async def confirming_chosen_news(message: Message, state: FSMContext):
    await state.update_data(news=message.text)
    await message.answer(
        text=message.text,
        reply_markup=yes_or_no()
    )
    await state.clear()


@router.callback_query(F.data == "yes")
async def news_confirm(callback: types.CallbackQuery, bot: Bot):
    msg = callback.message.answer("Начинаю рассылку")
    await callback.message.edit_reply_markup(None)
    for user in get_users():
        user_id = user[0]
        try:
            await bot.send_message(user_id, callback.message.text)
        except Exception as e:
            await callback.message.answer(f"Ошибка!\nID: {user_id}\nException: {e}")
    await msg.edit_text('Рассылка завершена')
    await callback.answer()


@router.callback_query(F.data == "no")
async def news_decline(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer("Отправка новости отменена")


@router.message(Command('return_users'))
async def users(message: Message):
    if is_admin(message.chat.id):
        res = ''
        for user in get_users():
            res += f"@{user[1]} - "
            res += f"ID: {user[0]}, "

            if user[2] == 0:
                res += "user, "
            else:
                res += "teacher, "
            res += f"{convert_role(user[-1])}\n"
        await message.answer(res)


@router.message(Command('logs'))
async def logs(
        message: Message,
        command: CommandObject
):
    if is_admin(message.chat.id):
        if command.args is None:
            lines = 10
        else:
            try:
                lines = int(command.args)
                if lines > 40:
                    await message.answer(
                        "Ошибка: кол-во строк не более 40"
                    )
                    return
            except ValueError:
                await message.answer(
                    "Ошибка: неверно переданы аргументы. Пример:\n/logs {кол-во строк лога}"
                )
                return
        res = ''
        with open('tmp.log') as f:
            for line in (f.readlines()[-lines:]):
                res += f"{line}\n"
        await message.answer(res)
