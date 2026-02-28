from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.keyboards.users import mentorship_menu, buy_mentor_btn, payment_options_btn, reuse_application_btn
from src.services.cryptopay_service import cryptopay_service
from src.database.models import Payment, User
from src.database.db import async_session
from src.utils.config import config
from sqlalchemy import select
from src.services.template_manager import template_manager
import logging

router = Router()


async def safe_edit_message(message: types.Message, text: str, **kwargs):
    """Try to edit a message's text or caption; fallback to sending a new message.

    This avoids "there is no text in the message to edit" errors when the
    original message contains media without text.
    """
    try:
        # If message has plain text, edit text
        if message.text is not None:
            return await message.edit_text(text, **kwargs)

        # If message has a caption (photo/video), edit caption
        if message.caption is not None:
            return await message.edit_caption(text, **kwargs)

        # Otherwise try edit_text and fallback
        return await message.edit_text(text, **kwargs)
    except TelegramBadRequest:
        try:
            # As a last resort, delete old message and send a new one
            await message.delete()
        except:  # keep best-effort
            pass
        return await message.bot.send_message(message.chat.id, text, **kwargs)

class ApplicationState(StatesGroup):
    waiting_for_answers = State()
    confirm_submission = State()

MENTORS = {
    "gatee": {
        "name": "🎗️ Gatee",
        "price": 1950,
        "reviews": "https://t.me/gatee_reviews", # Placeholder
        "desc": (
            "👨‍🏫 **Ментор Gatee**\n\n"
            "✅ Опыт в трейдинге: 5 лет\n"
            "✅ Объем торгов: >$10M\n"
            "✅ Специализация: Скальпинг и Интрадей\n\n"
            "В обучение входит:\n"
            "- 10 личных созвонов\n"
            "- Разбор вашей стратегии\n"
            "- Доступ в закрытый чат учеников\n\n"
            "💰 Стоимость: **1950 USDT** (150,000 RUB)"
        )
    },
    "agwwee": {
        "name": "👨‍💻 Agwwee",
        "price": 3900,
        "reviews": "https://t.me/agwwee_reviews", # Placeholder
        "desc": (
            "👨‍🏫 **Ментор Agwwee**\n\n"
            "✅ Опыт в трейдинге: 7 лет\n"
            "✅ Объем торгов: >$50M\n"
            "✅ Специализация: Алготрейдинг и Долгосрок\n\n"
            "В обучение входит:\n"
            "- Полное сопровождение до результата\n"
            "- Настройка торговых ботов\n"
            "- Персональный финансовый план\n\n"
            "💰 Стоимость: **3900 USDT** (300,000 RUB)"
        )
    }
}

@router.message(F.text == "🎓 Личное обучение")
async def show_mentors(message: types.Message):
    await template_manager.send_template(
        bot=message.bot,
        chat_id=message.chat.id,
        key="mentorship_main",
        reply_markup=mentorship_menu()
    )

@router.callback_query(F.data == "mentorship_start")
async def back_to_mentors(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
        
    await template_manager.send_template(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        key="mentorship_main",
        reply_markup=mentorship_menu()
    )

@router.callback_query(F.data.startswith("mentor_"))
async def show_mentor_details(callback: types.CallbackQuery):
    mentor_code = callback.data.split("_")[1]
    mentor = MENTORS.get(mentor_code)
    
    if not mentor:
        return

    await safe_edit_message(
        callback.message,
        mentor["desc"],
        reply_markup=buy_mentor_btn(mentor_code),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("reviews_"))
async def show_reviews(callback: types.CallbackQuery):
    mentor_code = callback.data.split("_")[1]
    mentor = MENTORS.get(mentor_code)
    
    await callback.answer("Открываю отзывы...", show_alert=False)
    # In real implementation, send photos or forward messages
    await callback.message.answer(
        f"⭐️ **Отзывы о {mentor['name']}**\n\n"
        "Ученики делают +30% к депозиту уже в первый месяц обучения.\n"
        f"Больше отзывов здесь: {mentor['reviews']}",
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("apply_mentor_"))
async def start_application(callback: types.CallbackQuery, state: FSMContext):
    # Format: apply_mentor_{code} OR apply_mentor_{code}_new
    parts = callback.data.split("_")
    mentor_code = parts[2]
    is_new = len(parts) > 3 and parts[3] == "new"
    
    await state.update_data(mentor_code=mentor_code)

    if not is_new:
        # Check if user has previous application
        async with async_session() as session:
            stmt = select(User).where(User.telegram_id == callback.from_user.id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user and user.last_application:
                await safe_edit_message(
                    callback.message,
                    "📝 **У вас уже есть заполненная анкета:**\n\n"
                    f"{user.last_application}\n\n"
                    "Хотите отправить её или заполнить заново?",
                    reply_markup=reuse_application_btn(mentor_code),
                    parse_mode="Markdown"
                )
                return

    await safe_edit_message(
        callback.message,
        "📝 **Анкета ученика**\n\n"
        "Пожалуйста, ответьте на несколько вопросов одним сообщением:\n"
        "1. Ваш опыт в трейдинге?\n"
        "2. Какой текущий депозит?\n"
        "3. Какая цель на обучение?\n\n"
        "Напишите ответы ниже:",
        parse_mode="Markdown"
    )
    await state.set_state(ApplicationState.waiting_for_answers)

@router.callback_query(F.data.startswith("reuse_app_"))
async def reuse_application(callback: types.CallbackQuery, state: FSMContext):
    mentor_code = callback.data.split("_")[2]
    
    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == callback.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user and user.last_application:
            await process_application_text(
                message=callback.message,
                user=callback.from_user,
                text=user.last_application,
                mentor_code=mentor_code,
                save_to_db=False # Already saved
            )
        else:
            await callback.answer("⚠️ Анкета не найдена. Заполните заново.", show_alert=True)
            await start_application(callback, state) # Redirect to new application

@router.message(ApplicationState.waiting_for_answers)
async def process_application_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    mentor_code = data.get("mentor_code")
    
    await process_application_text(
        message=message,
        user=message.from_user,
        text=message.text,
        mentor_code=mentor_code,
        save_to_db=True
    )
    await state.clear()

async def process_application_text(message: types.Message, user: types.User, text: str, mentor_code: str, save_to_db: bool = True):
    mentor = MENTORS.get(mentor_code)
    
    if save_to_db:
        async with async_session() as session:
            stmt = select(User).where(User.telegram_id == user.id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()
            if db_user:
                db_user.last_application = text
                await session.commit()

    # Send application to admins
    for admin_id in config.admins:
        try:
            await message.bot.send_message(
                admin_id,
                f"📝 **НОВАЯ АНКЕТА НА ОБУЧЕНИЕ**\n\n"
                f"👤 Кандидат: {user.full_name} (@{user.username})\n"
                f"👨‍🏫 Ментор: {mentor['name']}\n\n"
                f"📄 Ответы:\n{text}"
            )
        except: pass
        
    success_text = (
        "✅ **Анкета отправлена!**\n\n"
        "Теперь вы можете перейти к оплате. Выберите удобный вариант:"
    )
    
    # If called from button callback, edit message. If from text message, send new.
    if isinstance(message, types.Message) and message.text is not None and message.text == text: # It's a user message
        await message.answer(success_text, reply_markup=payment_options_btn(mentor_code), parse_mode="Markdown")
    else: # It's a bot message being edited (from reuse button)
        await safe_edit_message(message, success_text, reply_markup=payment_options_btn(mentor_code), parse_mode="Markdown")

@router.callback_query(F.data.startswith("pay_"))
async def process_buy_mentor(callback: types.CallbackQuery):
    # Format: pay_full_{code} OR pay_half_{code}
    parts = callback.data.split("_")
    payment_type = parts[1] # full or half
    mentor_code = parts[2]
    
    mentor = MENTORS.get(mentor_code)
    
    if not mentor:
        await callback.answer("⚠️ Ментор не найден.", show_alert=True)
        return

    price = mentor["price"]
    label = "Полная оплата"
    
    if payment_type == "half":
        price = price / 2
        label = "Рассрочка (50%)"

    invoice = await cryptopay_service.create_invoice(amount=price, currency="USDT")
    if not invoice:
        await callback.answer("⚠️ Ошибка создания счета. Попробуйте позже.", show_alert=True)
        return

    product_code = f"mentorship_{mentor_code}_{payment_type}"

    async with async_session() as session:
        payment = Payment(
            user_id=callback.from_user.id,
            amount=price,
            currency="USDT",
            crypto_pay_id=str(invoice.invoice_id),
            product_type=product_code
        )
        session.add(payment)
        await session.commit()

    await safe_edit_message(
        callback.message,
        f"💳 **Счет на оплату: {mentor['name']} ({label})**\n\n"
        f"Сумма к оплате: {price} USDT\n\n"
        "Нажмите кнопку ниже, чтобы перейти к оплате в @CryptoBot.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="💸 Оплатить", url=invoice.bot_invoice_url)],
            [types.InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_{invoice.invoice_id}_{product_code}")]
        ]),
        parse_mode="Markdown"
    )
