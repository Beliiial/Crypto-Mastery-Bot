from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.database.db import async_session
from src.database.models import User, Payment
from src.services.cryptopay_service import cryptopay_service
from src.services.payment_processing import process_successful_payment
from src.utils.config import config
from sqlalchemy import select
from datetime import datetime, timedelta
from src.services.template_manager import template_manager
from aiogram import Bot
import logging

async def check_pending_payments(bot: Bot):
    async with async_session() as session:
        # Get pending payments
        stmt = select(Payment).where(Payment.status == "pending")
        result = await session.execute(stmt)
        pending_payments = result.scalars().all()
        
        if not pending_payments:
            return

        # Prepare list of invoice IDs
        invoice_ids = [int(p.crypto_pay_id) for p in pending_payments if p.crypto_pay_id]
        
        if not invoice_ids:
            return

        # Check status in CryptoPay
        invoices = await cryptopay_service.get_invoices(invoice_ids=invoice_ids)
        
        for invoice in invoices:
            if invoice.status == "paid":
                # Find payment record
                payment = next((p for p in pending_payments if str(p.crypto_pay_id) == str(invoice.invoice_id)), None)
                if payment:
                    await process_successful_payment(bot, session, payment)


async def check_subscriptions(bot: Bot):
    async with async_session() as session:
        now = datetime.utcnow()
        stmt = select(User).where(
            User.has_active_subscription == True,
            User.subscription_end != None,
            User.subscription_end < now
        )
        result = await session.execute(stmt)
        expired_users = result.scalars().all()

        for user in expired_users:
            try:
                await bot.send_message(
                    user.telegram_id, 
                    "⚠️ Ваша подписка истекла. Продлите её в личном кабинете, чтобы сохранить доступ к каналу!"
                )
                user.has_active_subscription = False
                await session.commit()
            except Exception as e:
                logging.error(f"Error handling expired sub for {user.telegram_id}: {e}")

async def send_reminders(bot: Bot):
    async with async_session() as session:
        now = datetime.utcnow()
        
        # 1. Trial Follow-up
        # Users who got trial > 24h ago, no sub, no reminder sent
        cutoff_time = now - timedelta(hours=24)
        stmt = select(User).where(
            User.trial_received == True,
            User.trial_reminded == False,
            User.has_active_subscription == False,
            User.created_at < cutoff_time
        )
        result = await session.execute(stmt)
        trial_users = result.scalars().all()
        
        for user in trial_users:
            try:
                await template_manager.send_template(
                    bot=bot,
                    chat_id=user.telegram_id,
                    key="reminder_trial_24h"
                )
                user.trial_reminded = True
                await session.commit()
            except Exception as e:
                logging.error(f"Failed to send trial reminder to {user.telegram_id}: {e}")

        # 2. Subscription Expiry Reminders
        for days_left in [1, 3]:
            target_date = now + timedelta(days=days_left)
            stmt = select(User).where(
                User.subscription_end != None,
                User.subscription_end >= target_date,
                User.subscription_end < target_date + timedelta(days=1)
            )
            result = await session.execute(stmt)
            users_to_remind = result.scalars().all()

            for user in users_to_remind:
                try:
                    await bot.send_message(
                        user.telegram_id,
                        f"⏳ Ваша VIP-подписка истекает через {days_left} дня(ей). Не забудьте продлить её, чтобы сохранить доступ ко всем материалам!"
                    )
                except Exception as e:
                    logging.error(f"Failed to send expiry reminder to {user.telegram_id}: {e}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_subscriptions, "interval", hours=1, args=[bot])
    scheduler.add_job(send_reminders, "interval", hours=1, args=[bot])
    scheduler.add_job(check_pending_payments, "interval", minutes=1, args=[bot])
    scheduler.start()
    return scheduler
