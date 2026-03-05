from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.models import User, Payment
from src.utils.config import config
from src.utils.constants import TARIFS
from src.services.template_manager import template_manager
from datetime import datetime, timedelta
import logging

async def process_successful_payment(bot: Bot, session: AsyncSession, payment: Payment):
    """
    Process a successful payment: update user subscription, handle referral rewards,
    notify admins (if mentorship), and send confirmation to user.
    """
    if payment.status == "success":
        logging.info(f"Payment {payment.id} already processed.")
        return False

    payment.status = "success"
    
    # Fetch user to update subscription/check referral
    stmt = select(User).where(User.telegram_id == payment.user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        logging.error(f"User {payment.user_id} not found for payment {payment.id}")
        return False

    try:
        if "mentorship" in payment.product_type:
            await _handle_mentorship_payment(bot, session, user, payment)
        else:
            await _handle_subscription_payment(bot, session, user, payment)

        # Referral logic for ALL successful payments
        if user.referral_id:
            await _handle_referral_reward(bot, session, user, payment)

        await session.commit()
        return True
    except Exception as e:
        logging.error(f"Error processing payment {payment.id}: {e}")
        await session.rollback()
        return False

async def _handle_mentorship_payment(bot: Bot, session: AsyncSession, user: User, payment: Payment):
    # Notify admins
    for admin_id in config.admins:
        try:
            await bot.send_message(
                admin_id,
                f"🚨 **НОВАЯ ПОКУПКА ОБУЧЕНИЯ!**\n\n"
                f"👤 Покупатель: {user.full_name} (@{user.username})\n"
                f"🆔 ID: `{user.telegram_id}`\n"
                f"💰 Сумма: {payment.amount} USDT\n"
                f"🎓 Продукт: {payment.product_type}\n\n"
                "❗️ Свяжитесь с клиентом!"
            )
        except Exception as e:
            logging.error(f"Failed to notify admin {admin_id}: {e}")

    # Send confirmation to user
    chat_text = ""
    if config.STUDENT_CHAT_ID != 0:
        try:
            student_link = await bot.create_chat_invite_link(
                chat_id=config.STUDENT_CHAT_ID,
                member_limit=1
            )
            chat_text = f"\n🔗 Вступить в закрытый чат учеников: {student_link.invite_link}"
        except Exception as e:
            logging.error(f"Error creating student chat link: {e}")
            chat_text = "\n⚠️ Ссылка на чат будет отправлена администратором вручную."

    await template_manager.send_template(
        bot=bot,
        chat_id=user.telegram_id,
        key="mentorship_success",
        dynamic_text=f"{chat_text}\n\nЕсли у вас есть вопросы, нажмите кнопку 'Связаться с админом' в меню FAQ."
    )

async def _handle_subscription_payment(bot: Bot, session: AsyncSession, user: User, payment: Payment):
    tarif = TARIFS.get(payment.product_type)
    days = tarif["days"] if tarif else 30 # Fallback
    
    # Extend subscription
    now = datetime.utcnow()
    if user.subscription_end and user.subscription_end > now:
        user.subscription_end += timedelta(days=days)
    else:
        user.subscription_end = now + timedelta(days=days)
    
    user.has_active_subscription = True
    
    # Generate invite link
    try:
        invite_link = await bot.create_chat_invite_link(
            chat_id=config.CHANNEL_ID,
            member_limit=1
        )
        
        await template_manager.send_template(
            bot=bot,
            chat_id=user.telegram_id,
            key="payment_success",
            dynamic_text=(
                f"Ваша ссылка для входа в приватный канал:\n"
                f"{invite_link.invite_link}\n\n"
                "⚠️ Ссылка одноразовая. Не передавайте её никому!"
            )
        )
    except Exception as e:
        logging.error(f"Error creating invite link: {e}")
        await template_manager.send_template(
            bot=bot,
            chat_id=user.telegram_id,
            key="payment_success",
            dynamic_text="⚠️ Произошла ошибка при создании ссылки. Администратор свяжется с вами."
        )

async def _handle_referral_reward(bot: Bot, session: AsyncSession, user: User, payment: Payment):
    inviter_stmt = select(User).where(User.telegram_id == user.referral_id)
    inviter_result = await session.execute(inviter_stmt)
    inviter = inviter_result.scalar_one_or_none()
    
    if inviter:
        reward = payment.amount * 0.1 # 10% bonus
        inviter.balance += reward
        
        try:
            await template_manager.send_template(
                bot=bot,
                chat_id=inviter.telegram_id,
                key="referral_reward",
                dynamic_text=f"💰 +{reward:.2f} USDT (друг: {user.full_name})"
            )
        except Exception as e:
            logging.error(f"Failed to notify inviter {inviter.telegram_id}: {e}")
