from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.utils.config import config
from src.database.models import Base
from sqlalchemy import text
import logging

engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        # For simplicity in this task, we use create_all. 
        # In production, Alembic should be used.
        await conn.run_sync(Base.metadata.create_all)
        
        # Add column product_type to payments if not exists (quick fix for SQLite)
        if "sqlite" in config.DATABASE_URL:
            try:
                await conn.execute(text("ALTER TABLE payments ADD COLUMN product_type VARCHAR(32) DEFAULT 'subscription'"))
                logging.info("Added product_type column to payments table")
            except Exception:
                pass # Column likely exists
            
            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN last_application TEXT"))
                logging.info("Added last_application column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN trial_reminded BOOLEAN DEFAULT 0"))
                logging.info("Added trial_reminded column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(10)"))
                logging.info("Added avatar column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN funnel_step INTEGER DEFAULT 0"))
                logging.info("Added funnel_step column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN has_active_subscription BOOLEAN DEFAULT 0"))
                logging.info("Added has_active_subscription column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN trial_received BOOLEAN DEFAULT 0"))
                logging.info("Added trial_received column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN balance FLOAT DEFAULT 0.0"))
                logging.info("Added balance column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN referral_id BIGINT"))
                logging.info("Added referral_id column to users table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE messages ADD COLUMN media_url TEXT"))
                logging.info("Added media_url column to messages table")
            except Exception:
                pass # Column likely exists

            try:
                await conn.execute(text("ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT 0"))
                logging.info("Added is_read column to messages table")
            except Exception:
                pass # Column likely exists

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
