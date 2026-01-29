"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.services import get_model_manager


@pytest.fixture(scope="session", autouse=True)
def load_model():
    """Load models before running tests."""
    model_manager = get_model_manager()
    model_manager.load_all()
    yield
