from aiogram import Router, types, F
from aiogram.filters import Command
from src.utils.config import config
from src.database.models import User, Payment
from src.database.db import async_session
from sqlalchemy import select, func
import logging

router = Router()

# Middleware or simple check for admin
def is_admin(user_id: int):
    return user_id in config.admins

@router.message(Command("admin"))
async def admin_menu(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    async with async_session() as session:
        # Get statistics
        total_users = await session.execute(select(func.count(User.id)))
        total_payments = await session.execute(select(func.count(Payment.id)).where(Payment.status == "success"))
        total_revenue = await session.execute(select(func.sum(Payment.amount)).where(Payment.status == "success"))
        
        stats_text = (
            "👑 **Админ-панель**\n\n"
            f"📊 Пользователей: {total_users.scalar()}\n"
            f"💰 Оплат: {total_payments.scalar()}\n"
            f"💵 Выручка: {total_revenue.scalar() or 0} USDT\n\n"
            "Доступные команды:\n"
            "/content - Редактор контента и медиа\n"
            "/stats - Детальная статистика\n"
            "/broadcast - Рассылка (в разработке)\n"
            "/settings - Настройки бота"
        )
        
        await message.answer(stats_text, parse_mode="Markdown")

@router.message(Command("stats"))
async def detailed_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    # Here we could add more complex stats
    await message.answer("📊 Детальная статистика будет доступна здесь.")
