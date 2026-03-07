from datetime import datetime
from typing import Optional, List
from sqlalchemy import BigInteger, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    full_name: Mapped[str] = mapped_column(String(128))
    avatar: Mapped[Optional[str]] = mapped_column(String(10), default=None) # Emoji or char
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    referral_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    trial_received: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_reminded: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    subscription_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    has_active_subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    funnel_step: Mapped[int] = mapped_column(BigInteger, default=0) # 0, 1 (1 day), 2 (3 days), 3 (7 days)
    last_application: Mapped[Optional[str]] = mapped_column(Text)

    payments: Mapped[List["Payment"]] = relationship(back_populates="user")
    messages: Mapped[List["Message"]] = relationship(back_populates="user")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    product_type: Mapped[str] = mapped_column(String(32), default="subscription") # subscription, mentorship_gatee, mentorship_agwwee
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, success, failed
    crypto_pay_id: Mapped[Optional[str]] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="payments")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    mentor_id: Mapped[str] = mapped_column(String(32)) # support, gatee, agwwee
    text: Mapped[Optional[str]] = mapped_column(Text)
    media_url: Mapped[Optional[str]] = mapped_column(Text) # URL to photo
    sender: Mapped[str] = mapped_column(String(10)) # user, mentor
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="messages")

class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)

class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    inviter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    invitee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), unique=True)
    reward_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
