from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database.models import User
from src.database.db import async_session
from src.utils.config import config
from sqlalchemy import select
import logging
import asyncio

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_message = State()

@router.message(Command("broadcast"))
async def start_broadcast(message: types.Message, state: FSMContext):
    if message.from_user.id not in config.admins:
        return

    await message.answer("📝 Отправьте сообщение для рассылки (текст, фото или видео).")
    await state.set_state(BroadcastState.waiting_for_message)

@router.message(BroadcastState.waiting_for_message)
async def process_broadcast(message: types.Message, state: FSMContext):
    # Support text, photo, video, animation
    if not (message.text or message.photo or message.video or message.animation):
        await message.answer("⚠️ Поддерживается только текст, фото, видео или GIF.")
        return

    await state.clear()
    
    async with async_session() as session:
        stmt = select(User.telegram_id)
        result = await session.execute(stmt)
        user_ids = result.scalars().all()

    count = 0
    await message.answer(f"🚀 Начинаю рассылку на {len(user_ids)} пользователей...")
    
    for user_id in user_ids:
        try:
            # copy_to handles all media types automatically
            await message.copy_to(chat_id=user_id)
            count += 1
            await asyncio.sleep(0.05) # Anti-flood
        except Exception as e:
            logging.error(f"Failed to send broadcast to {user_id}: {e}")

    await message.answer(f"✅ Рассылка завершена! Получили: {count}/{len(user_ids)}")
