from aiogram import Router, types, F
from src.database.models import User
from src.database.db import async_session
from src.keyboards.users import profile_menu
from sqlalchemy import select, func
from src.services.template_manager import template_manager
from src.database.models import Referral
import logging

router = Router()

@router.message(F.text == "👤 Личный кабинет")
async def show_profile(message: types.Message):
    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == message.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return

        # Count referrals
        ref_stmt = select(func.count(User.id)).where(User.referral_id == message.from_user.id)
        ref_count_result = await session.execute(ref_stmt)
        ref_count = ref_count_result.scalar()

        sub_status = "❌ Неактивна"
        if user.sub_expires_at:
            sub_status = f"✅ Активна до {user.sub_expires_at.strftime('%d.%m.%Y')}"

        stats_text = (
            f"🆔 ID: `{user.telegram_id}`\n"
            f"💎 Подписка: {sub_status}\n"
            f"💰 Баланс бонусов: {user.balance} USDT\n"
            f"🤝 Приглашено друзей: {ref_count}\n\n"
            f"Ваша реферальная ссылка:\n"
            f"`t.me/{(await message.bot.get_me()).username}?start={user.telegram_id}`"
        )

        await template_manager.send_template(
            bot=message.bot,
            chat_id=message.chat.id,
            key="profile_info",
            dynamic_text=stats_text,
            reply_markup=profile_menu()
        )

@router.callback_query(F.data == "referral_info")
async def ref_info(callback: types.CallbackQuery):
    await callback.answer(
        "🤝 Приглашайте друзей по вашей ссылке и получайте 10% от их первой покупки на свой баланс!",
        show_alert=True
    )
