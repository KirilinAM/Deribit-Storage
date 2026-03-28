"""Shared pytest fixtures and configuration."""

from pathlib import Path

import pytest

@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent
