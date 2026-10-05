"""Manual Measurement Source.

Captures direct user input via keyboard, measurement table, or modal dialogs.
"""

from __future__ import annotations
from typing import Optional
from PySide6.QtCore import QObject

from measurement_sources.base import MeasurementSource


class ManualMeasurementSource(MeasurementSource):
    """Measurement source representing manual keyboard/GUI entry."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._is_connected = True

    def get_source_name(self) -> str:
        return "Manual Entry (Keyboard / Table)"

    def connect_source(self) -> bool:
        self._is_connected = True
        self.status_changed.emit("Manual entry ready.", True)
        return True

    def disconnect_source(self) -> None:
        self._is_connected = False
        self.status_changed.emit("Manual entry inactive.", False)

    def submit_reading(self, lux: float) -> None:
        """Manually trigger a lux measurement event."""
        if lux < 0:
            self.error_occurred.emit("Illuminance cannot be negative.")
            return
        self.measurement_received.emit(float(lux), self.get_source_name())
