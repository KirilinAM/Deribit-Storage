"""Shared pytest fixtures and configuration."""

from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import inspect

from src.core.database.models import PriceHistory


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def price_history_instance() -> PriceHistory:
    """Return a PriceHistory instance with default test values.

    ``id`` and ``created_at`` are intentionally omitted so that the
    model's ``default_factory`` callbacks are exercised.
    """
    return PriceHistory(
        ticker="BTC_USD",
        price=Decimal("50000.12345678"),
        timestamp=1710000000,
    )


@pytest.fixture
def price_history_mapper():
    """Return the SQLAlchemy mapper for PriceHistory."""
    return inspect(PriceHistory)
