"""Abstract Base Class for Measurement Sources.

Provides an event-driven Qt Signal architecture allowing manual input,
mock hardware testing, and future USB/Serial/Bluetooth lux meters.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from PySide6.QtCore import QObject, Signal


class MeasurementSource(QObject):
    """Abstract base class for all illuminance measurement input sources.

    Signals:
        measurement_received (float, str): Emitted when a new lux reading arrives (lux, source_name).
        status_changed (str, bool): Emitted when source status changes (message, is_connected).
        error_occurred (str): Emitted when an error occurs during reading.
    """
    measurement_received = Signal(float, str)
    status_changed = Signal(str, bool)
    error_occurred = Signal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._is_connected = False

    @abstractmethod
    def get_source_name(self) -> str:
        """Return human-readable name of the measurement device/source."""
        pass

    @abstractmethod
    def connect_source(self) -> bool:
        """Establish connection to measurement device."""
        pass

    @abstractmethod
    def disconnect_source(self) -> None:
        """Close connection to measurement device."""
        pass

    @property
    def is_connected(self) -> bool:
        """Return True if connection is active."""
        return self._is_connected
