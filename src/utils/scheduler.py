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
        # Find users with expired subscriptions
        now = datetime.utcnow()
        stmt = select(User).where(User.sub_expires_at < now)
        result = await session.execute(stmt)
        expired_users = result.scalars().all()

        for user in expired_users:
            try:
                # Remove from channel (unban after ban to just remove)
                # await bot.ban_chat_member(chat_id=config.CHANNEL_ID, user_id=user.telegram_id)
                # await bot.unban_chat_member(chat_id=config.CHANNEL_ID, user_id=user.telegram_id)
                
                await bot.send_message(
                    user.telegram_id, 
                    "⚠️ Ваша подписка истекла. Продлите её в личном кабинете, чтобы сохранить доступ к каналу!"
                )
                user.sub_expires_at = None
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
            User.sub_expires_at == None,
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
                # Commit immediately to save state
                await session.commit()
            except Exception as e:
                logging.error(f"Failed to send trial reminder to {user.telegram_id}: {e}")

        # 2. Subscription Expiry (3 days)
        target_3d = now + timedelta(days=3)
        window_start_3d = target_3d - timedelta(minutes=30)
        window_end_3d = target_3d + timedelta(minutes=30)
        
        stmt_3d = select(User).where(
            User.sub_expires_at >= window_start_3d,
            User.sub_expires_at <= window_end_3d
        )
        res_3d = await session.execute(stmt_3d)
        users_3d = res_3d.scalars().all()
        
        for user in users_3d:
            try:
                await template_manager.send_template(
                    bot=bot,
                    chat_id=user.telegram_id,
                    key="reminder_sub_3d"
                )
            except: pass
            
        # 3. Subscription Expiry (1 day)
        target_1d = now + timedelta(days=1)
        window_start_1d = target_1d - timedelta(minutes=30)
        window_end_1d = target_1d + timedelta(minutes=30)
        
        stmt_1d = select(User).where(
            User.sub_expires_at >= window_start_1d,
            User.sub_expires_at <= window_end_1d
        )
        res_1d = await session.execute(stmt_1d)
        users_1d = res_1d.scalars().all()
        
        for user in users_1d:
            try:
                await template_manager.send_template(
                    bot=bot,
                    chat_id=user.telegram_id,
                    key="reminder_sub_1d"
                )
            except: pass

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_subscriptions, "interval", hours=1, args=[bot])
    scheduler.add_job(send_reminders, "interval", hours=1, args=[bot])
    scheduler.add_job(check_pending_payments, "interval", minutes=1, args=[bot])
    scheduler.start()
    return scheduler
