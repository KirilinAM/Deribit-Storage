"""Database models for Deribit Storage."""

from decimal import Decimal
from datetime import datetime
import uuid

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.database import Base


class PriceHistory(Base):
    """Model for storing cryptocurrency price history."""
    
    __tablename__ = "price_history"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    ticker: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Cryptocurrency pair (e.g., btc_usd, eth_usd)",
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
        comment="Index price from Deribit",
    )
    timestamp: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="UNIX timestamp when price was recorded",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When the record was inserted in the database",
    )
    
    __table_args__ = (
        CheckConstraint(
            "ticker IN ('btc_usd', 'eth_usd')",
            name="valid_ticker",
        ),
        CheckConstraint(
            "price > 0",
            name="positive_price",
        ),
        CheckConstraint(
            "timestamp > 0",
            name="valid_timestamp",
        ),
    )
    
    def __repr__(self) -> str:
        return (
            f"PriceHistory(id={self.id!r}, ticker={self.ticker!r}, "
            f"price={self.price!r}, timestamp={self.timestamp!r})"
        )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "ticker": self.ticker,
            "price": float(self.price),
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }