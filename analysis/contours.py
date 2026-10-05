"""Isolux Contour Level Generator and Analysis.

Calculates standard isolux levels (e.g. 100 lx, 200 lx, 300 lx, 500 lx)
and manages contour intervals for visual plotting and report generation.
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Sequence
import numpy as np


def generate_isolux_levels(
    min_lux: float,
    max_lux: float,
    interval: Optional[float] = None,
    target_count: int = 8,
) -> np.ndarray:
    """Generate round, human-readable isolux contour levels.

    Args:
        min_lux: Minimum illuminance in dataset.
        max_lux: Maximum illuminance in dataset.
        interval: Optional fixed contour step (e.g., 25, 50, 100 lx).
        target_count: Target number of isolux lines if interval is None.

    Returns:
        1D NumPy array of sorted contour levels.
    """
    if np.isnan(min_lux) or np.isnan(max_lux) or min_lux >= max_lux:
        if not np.isnan(min_lux):
            return np.array([float(min_lux)])
        return np.array([])

    span = max_lux - min_lux

    if interval is not None and interval > 0:
        step = float(interval)
    else:
        # Determine nice standard step (e.g., 10, 20, 25, 50, 100, 200, 500, 1000)
        raw_step = span / max(1, target_count)
        nice_steps = [5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 150.0, 200.0, 250.0, 500.0, 1000.0]
        step = nice_steps[0]
        for s in nice_steps:
            if s >= raw_step:
                step = s
                break
        if raw_step > nice_steps[-1]:
            step = round(raw_step / 100.0) * 100.0

    start = np.floor(min_lux / step) * step
    end = np.ceil(max_lux / step) * step

    levels = np.arange(start, end + step * 0.5, step)
    # Filter within [min_lux, max_lux] or slightly extended
    levels = levels[(levels >= min_lux - 1e-3) & (levels <= max_lux + 1e-3)]

    if len(levels) < 2:
        levels = np.linspace(min_lux, max_lux, max(2, min(5, target_count)))

    return np.unique(np.round(levels, 2))
