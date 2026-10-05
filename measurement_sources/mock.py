"""Mock / Simulation Lux Meter Source.

Useful for testing hardware event hooks and simulating physical lux meter streams.
"""

from __future__ import annotations
from typing import Optional
import random
from PySide6.QtCore import QObject, QTimer

from measurement_sources.base import MeasurementSource


class MockLuxMeterSource(MeasurementSource):
    """Simulated hardware lux meter for testing and demonstration."""

    def __init__(
        self,
        base_lux: float = 450.0,
        noise_std: float = 25.0,
        interval_ms: int = 1500,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self.base_lux = base_lux
        self.noise_std = noise_std
        self.interval_ms = interval_ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._generate_reading)

    def get_source_name(self) -> str:
        return "Mock Lux Meter (Simulation)"

    def connect_source(self) -> bool:
        self._is_connected = True
        self._timer.start(self.interval_ms)
        self.status_changed.emit("Mock Lux Meter connected (Streaming).", True)
        return True

    def disconnect_source(self) -> None:
        self._timer.stop()
        self._is_connected = False
        self.status_changed.emit("Mock Lux Meter disconnected.", False)

    def _generate_reading(self) -> None:
        if not self._is_connected:
            return
        val = max(0.0, random.gauss(self.base_lux, self.noise_std))
        self.measurement_received.emit(round(val, 1), self.get_source_name())
