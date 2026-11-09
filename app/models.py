from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Enquiry(Base):
    __tablename__ = "enquiries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(String(40), default="")
    property_address: Mapped[str] = mapped_column(String(300))
    property_type: Mapped[str] = mapped_column(String(40), default="Detached")
    approximate_size_sqft: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, default="")
    preferred_dates: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class BookingProposal(Base):
    __tablename__ = "booking_proposals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enquiry_id: Mapped[int] = mapped_column(Integer, index=True)
    option_1: Mapped[str] = mapped_column(String(80), default="")
    option_2: Mapped[str] = mapped_column(String(80), default="")
    option_3: Mapped[str] = mapped_column(String(80), default="")
    status: Mapped[str] = mapped_column(String(30), default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class QuoteSettings(Base):
    __tablename__ = "quote_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    base_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    per_sqft_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    minimum_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class QuoteDraft(Base):
    __tablename__ = "quote_drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enquiry_id: Mapped[int] = mapped_column(Integer, index=True)
    property_type: Mapped[str] = mapped_column(String(40))
    size_sqft: Mapped[int] = mapped_column(Integer)
    base_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    per_sqft_rate: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    minimum_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="CAD")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    note: Mapped[str] = mapped_column(String(300), default="Tax, travel, and special circumstances are not included.")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
