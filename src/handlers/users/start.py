from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from src.database.models import User
from src.database.db import async_session
from sqlalchemy import select
from src.keyboards.users import main_menu
from src.utils.config import config
import logging

from src.services.template_manager import template_manager

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    # Extract referral ID if present
    args = message.text.split()
    referral_id = None
    if len(args) > 1 and args[1].isdigit():
        referral_id = int(args[1])
        if referral_id == message.from_user.id:
            referral_id = None

    async with async_session() as session:
        # Check if user exists
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
                referral_id=referral_id
            )
            session.add(user)
            await session.commit()
            logging.info(f"New user: {message.from_user.id} (ref: {referral_id})")

        await template_manager.send_template(
            bot=message.bot,
            chat_id=message.chat.id,
            key="start_welcome",
            reply_markup=main_menu(has_trial=user.trial_received)
        )

@router.message(F.text == "🎁 Получить пробный урок")
async def get_trial(message: types.Message):
    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return # User should exist after /start

        if user.trial_received:
            await message.answer("❌ Вы уже получили пробный урок. Купите доступ, чтобы получить больше!")
            return

        # Send trial template
        success = await template_manager.send_template(
            bot=message.bot,
            chat_id=message.chat.id,
            key="trial_delivered"
        )

        if success:
            user.trial_received = True
            await session.commit()
            
            # Send updated menu without "Get Trial" button
            await message.answer(
                "✅ Пробный урок выдан. Меню обновлено.",
                reply_markup=main_menu(has_trial=True)
            )
        else:
            await message.answer("⚠️ Ошибка при отправке урока. Пожалуйста, попробуйте позже.")
