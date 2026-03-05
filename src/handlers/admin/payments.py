from aiogram import Router, types, F
from src.database.db import async_session
from src.database.models import Payment, User
from src.services.payment_processing import process_successful_payment
from src.utils.config import config
from sqlalchemy import select
import logging

router = Router()

def is_admin(user_id: int):
    return user_id in config.admins

@router.callback_query(F.data.startswith("admin_pay_approve_"))
async def approve_manual_payment(callback: types.CallbackQuery):
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

        # Process the payment
        # Note: process_successful_payment handles status update and user notification
        success = await process_successful_payment(callback.bot, session, payment)
        if success:
            await session.commit()
            
            # Update admin message
            try:
                await callback.message.edit_text(
                    f"{callback.message.text}\n\n✅ **ПОДТВЕРЖДЕНО** администратором {callback.from_user.full_name}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Error editing admin message: {e}")
                
            await callback.answer("Платеж успешно подтвержден!", show_alert=True)
        else:
            await callback.answer("Ошибка при обработке платежа.", show_alert=True)

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
