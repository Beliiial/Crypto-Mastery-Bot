from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database.db import async_session
from src.database.models import Payment, User
from src.utils.config import config
from sqlalchemy import select
from datetime import datetime, timedelta
import logging

router = Router()

def is_admin(user_id: int):
    return user_id in config.admins

class ManualPaymentState(StatesGroup):
    waiting_days = State()

@router.callback_query(F.data.startswith("admin_pay_received_"))
async def admin_pay_received(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    payment_id = callback.data.split("_")[-1]

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="1 Месяц", callback_data=f"grant_days_{payment_id}_30"),
            types.InlineKeyboardButton(text="3 Месяца", callback_data=f"grant_days_{payment_id}_90")
        ],
        [
            types.InlineKeyboardButton(text="Навсегда", callback_data=f"grant_days_{payment_id}_0"),
            types.InlineKeyboardButton(text="Вручную", callback_data=f"grant_custom_{payment_id}")
        ],
        [
            types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin_pay_back_{payment_id}")
        ]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=kb)

@router.callback_query(F.data.startswith("admin_pay_back_"))
async def admin_pay_back(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    payment_id = callback.data.split("_")[-1]

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Оплата пришла", callback_data=f"admin_pay_received_{payment_id}"),
            types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_pay_reject_{payment_id}")
        ]
    ])
    
    await callback.message.edit_reply_markup(reply_markup=kb)

@router.callback_query(F.data.startswith("grant_days_"))
async def grant_specific_days(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    parts = callback.data.split("_")
    payment_id = int(parts[2])
    days = int(parts[3])

    async with async_session() as session:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            await callback.answer("Платеж не найден.", show_alert=True)
            return

        if payment.status == "success":
            await callback.answer("Этот платеж уже подтвержден.", show_alert=True)
            return
            
        # Get user
        user_stmt = select(User).where(User.telegram_id == payment.user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Пользователь не найден.", show_alert=True)
            return

        now = datetime.utcnow()
        human_days = ""
        
        if days == 0:
            user.subscription_end = None
            user.has_active_subscription = True
            human_days = "Бессрочно"
        else:
            if user.subscription_end and user.subscription_end > now:
                user.subscription_end += timedelta(days=days)
            else:
                user.subscription_end = now + timedelta(days=days)
            user.has_active_subscription = True
            human_days = f"{days} дн."

        payment.status = "success"
        await session.commit()
        
        # Notify user
        try:
            invite_text = ""
            if config.CHANNEL_ID != 0: # Assuming channel ID is set
                 # Only create invite link if we have channel ID. 
                 # Note: handling invite links in callback might be slow, but ok for now.
                 pass

            await callback.bot.send_message(
                payment.user_id,
                f"✅ Оплата подтверждена. Подписка выдана: {human_days}."
            )
        except Exception as e:
            logging.error(f"Error notifying user: {e}")
            
        # Update admin message
        try:
            await callback.message.edit_text(
                f"{callback.message.text}\n\n✅ **ПОДТВЕРЖДЕНО** ({human_days}) администратором {callback.from_user.full_name}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error editing admin message: {e}")

@router.callback_query(F.data.startswith("grant_custom_"))
async def grant_custom(callback: types.CallbackQuery, state: FSMContext):
    # Reuse existing logic logic by redirecting to request_manual_days logic
    # We just need to change the callback data to match what request_manual_days expects 
    # OR we can just call the function directly if we extract the logic.
    # But for simplicity, let's just copy the logic or call it.
    
    # Construct a fake callback with correct data format if we were to reuse
    # But it's better to just implement it here cleanly.
    
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    payment_id = int(callback.data.split("_")[-1])

    await state.update_data(
        payment_id=payment_id,
        admin_message_id=callback.message.message_id,
        admin_chat_id=callback.message.chat.id,
        admin_message_text=callback.message.text
    )
    await callback.message.answer("Введите количество дней подписки (0 = бессрочно).")
    await state.set_state(ManualPaymentState.waiting_days)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_pay_grant_"))
async def request_manual_days(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    payment_id = int(callback.data.split("_")[-1])

    async with async_session() as session:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            await callback.answer("Платеж не найден.", show_alert=True)
            return

        if payment.status == "success":
            await callback.answer("Этот платеж уже подтвержден.", show_alert=True)
            return

        if payment.status != "manual_pending":
            await callback.answer(f"Нельзя подтвердить платеж со статусом {payment.status}", show_alert=True)
            return

    await state.update_data(
        payment_id=payment_id,
        admin_message_id=callback.message.message_id,
        admin_chat_id=callback.message.chat.id,
        admin_message_text=callback.message.text
    )
    await callback.message.answer("Введите количество дней подписки (0 = бессрочно).")
    await state.set_state(ManualPaymentState.waiting_days)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_pay_reject_"))
async def reject_manual_payment(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав для этого действия.", show_alert=True)
        return

    payment_id = int(callback.data.split("_")[-1])
    
    async with async_session() as session:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()
        
        if not payment:
            await callback.answer("Платеж не найден.", show_alert=True)
            return
            
        if payment.status != "manual_pending":
            await callback.answer(f"Нельзя отклонить платеж со статусом {payment.status}", show_alert=True)
            return

        payment.status = "failed"
        await session.commit()
        
        # Update admin message
        try:
            await callback.message.edit_text(
                f"{callback.message.text}\n\n❌ **ОТКЛОНЕНО** администратором {callback.from_user.full_name}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error editing admin message: {e}")
        
        # Notify user
        try:
            await callback.bot.send_message(
                payment.user_id,
                "❌ Ваша заявка на ручную оплату была отклонена администратором.\n"
                "Если у вас есть вопросы, свяжитесь с поддержкой."
            )
        except Exception as e:
            logging.error(f"Error notifying user about rejection: {e}")
        
        await callback.answer("Заявка отклонена.", show_alert=True)

@router.message(ManualPaymentState.waiting_days)
async def apply_manual_days(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    data = await state.get_data()
    payment_id = data.get("payment_id")
    admin_message_id = data.get("admin_message_id")
    admin_chat_id = data.get("admin_chat_id")
    admin_message_text = data.get("admin_message_text") or ""

    try:
        days = int(message.text.strip())
        if days < 0:
            raise ValueError()
    except Exception:
        await message.answer("Введите корректное число дней (0 или больше).")
        return

    async with async_session() as session:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            await message.answer("Платеж не найден.")
            await state.clear()
            return

        if payment.status == "success":
            await message.answer("Этот платеж уже подтвержден.")
            await state.clear()
            return

        user_stmt = select(User).where(User.telegram_id == payment.user_id)
        user_result = await session.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            await message.answer("Пользователь не найден.")
            await state.clear()
            return

        now = datetime.utcnow()
        if days == 0:
            user.subscription_end = None
            user.has_active_subscription = True
            human_days = "Бессрочно"
        else:
            if user.subscription_end and user.subscription_end > now:
                user.subscription_end += timedelta(days=days)
            else:
                user.subscription_end = now + timedelta(days=days)
            user.has_active_subscription = True
            human_days = f"{days} дн."

        payment.status = "success"
        await session.commit()

    invite_text = ""
    if config.CHANNEL_ID != 0:
        try:
            invite_link = await message.bot.create_chat_invite_link(
                chat_id=config.CHANNEL_ID,
                member_limit=1
            )
            invite_text = f"\n🔗 Ссылка для входа в канал: {invite_link.invite_link}"
        except Exception as e:
            logging.error(f"Error creating invite link: {e}")

    try:
        await message.bot.send_message(
            payment.user_id,
            f"✅ Оплата подтверждена. Подписка выдана: {human_days}.{invite_text}"
        )
    except Exception as e:
        logging.error(f"Error notifying user about approval: {e}")

    if admin_message_id and admin_chat_id:
        try:
            await message.bot.edit_message_text(
                chat_id=admin_chat_id,
                message_id=admin_message_id,
                text=f"{admin_message_text}\n\n✅ **ПОДТВЕРЖДЕНО** ({human_days}) администратором {message.from_user.full_name}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Error editing admin message: {e}")

    await message.answer("Подписка выдана.")
    await state.clear()
