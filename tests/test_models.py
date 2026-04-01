"""Tests for SQLAlchemy database models."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID

from src.core.database.models import PriceHistory


class TestPriceHistoryModel:
    """Tests for PriceHistory SQLAlchemy model."""

    def test_table_name(self):
        """Model must map to the 'price_history' table."""
        assert PriceHistory.__tablename__ == "price_history"

    def test_model_inherits_from_base(self):
        """PriceHistory must be a mapped class registered with Base."""
        assert PriceHistory.__mapper__.class_ is PriceHistory

    @pytest.mark.parametrize(
        "col_name,expected_type_cls,nullable,primary_key",
        [
            ("id", PgUUID, False, True),
            ("ticker", String, False, False),
            ("price", Numeric, False, False),
            ("timestamp", BigInteger, False, False),
            ("created_at", DateTime, False, False),
        ],
        ids=["id", "ticker", "price", "timestamp", "created_at"],
    )
    def test_column_exists_with_correct_properties(
        self, price_history_mapper, col_name, expected_type_cls, nullable, primary_key
    ):
        """Each column must exist with the expected type, nullability, and PK flag."""
        assert (
            col_name in price_history_mapper.columns
        ), f"Column '{col_name}' is missing"

        col = price_history_mapper.columns[col_name]
        assert (
            col.nullable is nullable
        ), f"Column '{col_name}' nullable expected {nullable}, got {col.nullable}"
        assert col.primary_key is primary_key, (
            f"Column '{col_name}' primary_key expected {primary_key}, "
            f"got {col.primary_key}"
        )
        assert isinstance(col.type, expected_type_cls), (
            f"Column '{col_name}' type expected {expected_type_cls.__name__}, "
            f"got {type(col.type).__name__}"
        )

    def test_id_default_generates_uuid4(self, price_history_instance):
        """Creating an instance without id must auto-generate a UUID4."""
        assert isinstance(price_history_instance.id, uuid.UUID)
        assert price_history_instance.id.version == 4

    def test_created_at_default_is_timezone_aware(self, price_history_instance):
        """Creating an instance without created_at must auto-generate a tz-aware datetime."""
        assert isinstance(price_history_instance.created_at, datetime)
        assert (
            price_history_instance.created_at.tzinfo is not None
        ), "created_at default must be timezone-aware"
