from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.utils.config import config
from src.database.models import User
from src.database.db import async_session
from sqlalchemy import select, update
from datetime import datetime, timedelta

router = Router()
router.message.filter(F.from_user.id.in_(config.admins))

class GrantAccess(StatesGroup):
    user_id = State()
    days = State()

@router.message(Command("grant_access"))
async def grant_access_start(message: types.Message, state: FSMContext):
    await message.answer("Введите Telegram ID пользователя, которому нужно выдать подписку:")
    await state.set_state(GrantAccess.user_id)

@router.message(GrantAccess.user_id)
async def grant_access_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await message.answer("На сколько дней выдать подписку? (0 - навсегда)")
        await state.set_state(GrantAccess.days)
    except ValueError:
        await message.answer("Неверный ID. Попробуйте еще раз.")

@router.message(GrantAccess.days)
async def grant_access_days(message: types.Message, state: FSMContext):
    try:
        days = int(message.text)
        data = await state.get_data()
        user_id = data.get("user_id")

        async with async_session() as session:
            stmt = select(User).where(User.telegram_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                await message.answer(f"Пользователь с ID {user_id} не найден.")
                await state.clear()
                return

            if days == 0:
                new_sub_end = None # Forever
                sub_end_str = "навсегда"
            else:
                new_sub_end = datetime.utcnow() + timedelta(days=days)
                sub_end_str = f"на {days} дней"

            await session.execute(
                update(User)
                .where(User.telegram_id == user_id)
                .values(subscription_end=new_sub_end, has_active_subscription=True)
            )
            await session.commit()

        await message.answer(f"✅ Подписка успешно выдана пользователю {user_id} {sub_end_str}.")
        try:
            await message.bot.send_message(
                user_id,
                f"🎉 Вам выдана VIP-подписка {sub_end_str}!"
            )
        except Exception:
            await message.answer("Не удалось уведомить пользователя.")

        await state.clear()

    except ValueError:
        await message.answer("Неверное количество дней. Введите число.")
