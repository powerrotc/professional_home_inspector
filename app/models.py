from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text
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
