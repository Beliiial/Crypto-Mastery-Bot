from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from src.database.models import User, Payment
from src.database.db import async_session
from sqlalchemy import select
from src.keyboards.users import main_menu, mentorship_menu
from src.utils.config import config
from src.services.cryptopay_service import cryptopay_service
from src.utils.constants import TARIFS
from src.handlers.users.mentorship import MENTORS
import logging
import json
from datetime import datetime

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
        is_new = False

        if not user:
            is_new = True
            try:
                user = User(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    full_name=message.from_user.full_name,
                    referral_id=referral_id
                )
                session.add(user)
                await session.commit()
                logging.info(f"New user created: {message.from_user.id}")
            except Exception as e:
                logging.error(f"Failed to create user {message.from_user.id}: {e}")
                # Try to fetch again in case of race condition
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    is_new = False

        if is_new:
            # Registration offer for new users
            logging.info(f"Showing registration offer for new user {message.from_user.id}")
            await message.answer(
                f"👋 **Привет, {message.from_user.first_name}!**\n\n"
                "Ты успешно зарегистрирован в Gatee Bot. Мы — команда экспертов в арбитраже криптовалют.\n\n"
                "🎁 Для старта мы подготовили для тебя **бесплатный пробный урок**!\n"
                "Жми кнопку ниже, чтобы забрать его 👇",
                reply_markup=main_menu(has_trial=False)
            )
        else:
            logging.info(f"Showing main menu for existing user {message.from_user.id}")
            if user:
                await template_manager.send_template(
                    bot=message.bot,
                    chat_id=message.chat.id,
                    key="start_welcome",
                    reply_markup=main_menu(has_trial=user.trial_received)
                )

@router.message(F.web_app_data)
async def process_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        plan_id = data.get("plan_id")
        
        if action == "create_invoice":
            # Determine price and label
            price = 0
            label = ""
            
            if plan_id in TARIFS:
                price = TARIFS[plan_id]["amount"]
                label = TARIFS[plan_id]["label"]
            elif plan_id.startswith("mentorship_"):
                # mentorship_{mentor}_{type}
                parts = plan_id.split("_")
                mentor_code = parts[1]
                payment_type = parts[2] # full or half
                
                mentor = MENTORS.get(mentor_code)
                if mentor:
                    price = mentor["price"]
                    label = f"{mentor['name']} (Полная)"
                    if payment_type == "half":
                        price = price / 2
                        label = f"{mentor['name']} (50%)"

            if price > 0:
                invoice = await cryptopay_service.create_invoice(amount=price, currency="USDT")
                if invoice:
                    async with async_session() as session:
                        payment = Payment(
                            user_id=message.from_user.id,
                            amount=price,
                            currency="USDT",
                            crypto_pay_id=str(invoice.invoice_id),
                            product_type=plan_id
                        )
                        session.add(payment)
                        await session.commit()

                    await message.answer(
                        f"✅ Счет на оплату создан!\n\n"
                        f"📦 Товар: {label}\n"
                        f"💰 Сумма: {price} USDT\n\n"
                        f"Оплатите по кнопке ниже:",
                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="💸 Оплатить", url=invoice.bot_invoice_url)],
                            [types.InlineKeyboardButton(text="✅ Проверить оплату", callback_data=f"check_{invoice.invoice_id}_{plan_id}")]
                        ])
                    )
                else:
                    await message.answer("⚠️ Ошибка создания счета CryptoBot.")
            else:
                await message.answer("⚠️ Выбранный тариф не найден.")

        elif action == "manual_payment":
            method = data.get("method") or "unknown"
            amount = data.get("amount")
            currency = data.get("currency") or "USDT"
            wallet_address = data.get("wallet_address")
            
            price = 0
            label = ""
            if plan_id in TARIFS:
                price = TARIFS[plan_id]["amount"]
                label = TARIFS[plan_id]["label"]
            elif plan_id.startswith("mentorship_"):
                parts = plan_id.split("_")
                mentor_code = parts[1]
                payment_type = parts[2]
                
                mentor = MENTORS.get(mentor_code)
                if mentor:
                    price = mentor["price"]
                    label = f"{mentor['name']} (Полная)"
                    if payment_type == "half":
                        price = price / 2
                        label = f"{mentor['name']} (50%)"

            if isinstance(amount, (int, float)):
                price = amount
            elif isinstance(amount, str):
                try:
                    price = float(amount)
                except Exception:
                    pass

            async with async_session() as session:
                payment = Payment(
                    user_id=message.from_user.id,
                    amount=price,
                    currency=currency,
                    product_type=plan_id,
                    status="manual_pending",
                    crypto_pay_id=f"manual_{message.from_user.id}_{int(datetime.utcnow().timestamp())}"
                )
                session.add(payment)
                await session.commit()
                await session.refresh(payment)
                payment_id = payment.id

            admin_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="Оплата пришла", callback_data=f"admin_pay_received_{payment_id}"),
                    types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_pay_reject_{payment_id}")
                ]
            ])

            wallet_line = f"\n🏦 Кошелек: `{wallet_address}`" if wallet_address else ""

            for admin_id in config.admins:
                try:
                    await message.bot.send_message(
                        admin_id,
                        f"🔔 **ЗАЯВКА НА РУЧНУЮ ОПЛАТУ (WebApp)**\n\n"
                        f"👤 Пользователь: {message.from_user.full_name} (@{message.from_user.username or 'No username'})\n"
                        f"🆔 ID: `{message.from_user.id}`\n"
                        f"📦 Тариф: {label or plan_id}\n"
                        f"💰 Сумма: {price} {currency}\n"
                        f"🕒 Дата: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
                        f"💳 Метод: {method.upper()}{wallet_line}\n"
                        f"🧾 ID Заявки: `{payment_id}`",
                        parse_mode="Markdown",
                        reply_markup=admin_kb
                    )
                except Exception as e:
                    logging.error(f"Failed to notify admin {admin_id}: {e}")

            await message.answer("✅ Ваша заявка на оплату принята!\nОжидайте подтверждения администратором.")

        elif action == "chat_message":
            mentor_id = data.get("mentor_id")
            text = data.get("text")
            if not mentor_id or not text:
                return

            for admin_id in config.admins:
                try:
                    await message.bot.send_message(
                        admin_id,
                        f"💬 **Новое сообщение из WebApp**\n\n"
                        f"👤 Пользователь: {message.from_user.full_name} (@{message.from_user.username or 'No username'})\n"
                        f"🆔 ID: `{message.from_user.id}`\n"
                        f"👨‍🏫 Чат: {mentor_id}\n"
                        f"✉️ Сообщение:\n{text}",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logging.error(f"Failed to forward chat message to admin {admin_id}: {e}")

    except Exception as e:
        logging.error(f"Error processing WebApp data: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке данных из WebApp.")

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
