from aiogram import Router, F, types
from database import commands
from keyboards.questions import select_role, select_stage

router = Router()


@router.callback_query(F.data.startswith("role_"))
async def query(callback: types.CallbackQuery):
    if commands.check_existing(callback.message.chat.id):
        role = callback.data.split('_')[1]
        commands.add_user(callback.message.chat.id, callback.message.chat.username, role)
        await callback.message.delete()
        await callback.message.answer(
            "Поздравляем, теперь вам доступны материалы для подготовки по вашему направлению\n\nВоспользуйтесь нижней "
            "клавиатурой для выбора материалов", reply_markup=select_stage()
        )
        await callback.answer()
    else:
        # TODO: move to authorization handler
        await callback.message.answer(
            "Выбери свое направление",
            reply_markup=select_role()
        )
