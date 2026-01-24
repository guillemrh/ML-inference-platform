"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.models import get_model


@pytest.fixture(scope="session", autouse=True)
def load_model():
    """Load model before running tests."""
    model = get_model()
    if not model.is_loaded:
        model.load()
    yield
