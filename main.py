import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.utils.config import config
from src.handlers.users import start, payments, profile, support, mentorship
from src.handlers.admin import menu, broadcast, content, payments as admin_payments
from src.handlers.admins import access
from src.database.db import init_db
from src.utils.scheduler import setup_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def main():
    # Initialize database
    logging.info("Initializing database...")
    await init_db()

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Setup scheduler
    scheduler = setup_scheduler(bot)

    # Include routers
    dp.include_router(menu.router)
    dp.include_router(broadcast.router)
    dp.include_router(content.router)
    dp.include_router(admin_payments.router)
    dp.include_router(access.router)
    dp.include_router(start.router)
    dp.include_router(payments.router)
    dp.include_router(profile.router)
    dp.include_router(support.router)
    dp.include_router(mentorship.router)

    # Start polling
    logging.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
