from aiogram import Router, types, F
from src.database.models import User, Payment
from src.database.db import async_session
from src.services.cryptopay_service import cryptopay_service
from src.keyboards.users import buy_menu
from src.utils.config import config
from src.utils.constants import TARIFS
from src.services.payment_processing import process_successful_payment
from sqlalchemy import select
from datetime import datetime, timedelta
import logging

from src.services.template_manager import template_manager

router = Router()

@router.message(F.text == "💎 Купить доступ")
async def show_tarifs(message: types.Message):
    await template_manager.send_template(
        bot=message.bot,
        chat_id=message.chat.id,
        key="tarifs_list",
        reply_markup=buy_menu()
    )

@router.callback_query(F.data == "buy_access")
async def show_tarifs_callback(callback: types.CallbackQuery):
    # Since we can't easily edit a text message into a photo message via standard edit_text if type changes,
    # and template might have media, send_template handles this logic (if called as edit replacement).
    # But here we are just sending a new message or answering.
    # The callback comes from a menu. Let's send a new message for visibility or edit?
    # Original code was message.answer (new message).
    
    await template_manager.send_template(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        key="tarifs_list",
        reply_markup=buy_menu()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    tarif_id = callback.data
    tarif = TARIFS.get(tarif_id)
    
    if not tarif:
        return

    invoice = await cryptopay_service.create_invoice(tarif["amount"])
    if not invoice:
        await callback.answer("⚠️ Ошибка создания счета. Попробуйте позже.", show_alert=True)
        return

    async with async_session() as session:
        payment = Payment(
            user_id=callback.from_user.id,
            amount=tarif["amount"],
            currency="USDT",
            crypto_pay_id=str(invoice.invoice_id),
            product_type=tarif_id # "buy_1_month", etc.
        )
        session.add(payment)
        await session.commit()

    # We need to edit the previous message or send new. Original was edit_text.
    # But template might have media.
    # Let's delete the previous message and send a new one to be safe with media templates.
    try:
        await callback.message.delete()
    except:
        pass

    dynamic_text = (
        f"\n📋 Тариф: {tarif['label']}\n"
        f"💰 Сумма: {tarif['amount']} USDT"
    )

    await template_manager.send_template(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        key="invoice_created",
        dynamic_text=dynamic_text,
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💸 Оплатить", url=invoice.bot_invoice_url)],
            [types.InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_{invoice.invoice_id}_{tarif_id}")]
        ])
    )

@router.callback_query(F.data.startswith("check_"))
async def check_payment(callback: types.CallbackQuery):
    # Format: check_{invoice_id}_{product_code}
    # But product_code can contain underscores (e.g. mentorship_gatee_full)
    # So we split by maxsplit=2
    parts = callback.data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("⚠️ Неверные данные кнопки.", show_alert=True)
        return
        
    invoice_id = parts[1]
    product_code = parts[2]
    
    invoice = await cryptopay_service.get_invoice(int(invoice_id))
    if not invoice:
        await callback.answer("⚠️ Счет не найден.", show_alert=True)
        return

    if invoice.status == "paid":
        async with async_session() as session:
            # Update payment status
            stmt = select(Payment).where(Payment.crypto_pay_id == str(invoice_id))
            result = await session.execute(stmt)
            payment = result.scalar_one_or_none()
            
            if payment:
                if payment.status != "success":
                    success = await process_successful_payment(callback.bot, session, payment)
                    if success:
                        # Message is already sent by process_successful_payment, 
                        # but we might want to update the original message too or delete it.
                        # The original message has the "Check Payment" button.
                        # Let's just answer the callback.
                        await callback.answer("✅ Оплата успешно подтверждена!", show_alert=True)
                        try:
                            await callback.message.delete()
                        except:
                            pass
                    else:
                        await callback.answer("⚠️ Произошла ошибка при обработке.", show_alert=True)
                else:
                    await callback.answer("✅ Оплата уже обработана.", show_alert=True)
            else:
                await callback.answer("⚠️ Платеж не найден в базе.", show_alert=True)
    else:
        await callback.answer("⏳ Оплата еще не поступила.", show_alert=True)
