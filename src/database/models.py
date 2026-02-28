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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    referral_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.telegram_id"))
    trial_received: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_reminded: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    sub_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_application: Mapped[Optional[str]] = mapped_column(Text)

    payments: Mapped[List["Payment"]] = relationship(back_populates="user")

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
