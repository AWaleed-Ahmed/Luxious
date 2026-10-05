"""Pytest configuration and shared fixtures for Lumination."""

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Ensure a single QApplication instance exists for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
