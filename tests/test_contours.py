"""Unit tests for Isolux Contour Generation."""

import numpy as np
from analysis.contours import generate_isolux_levels


def test_contour_levels_generation():
    """Verify round contour level generation with fixed and automatic steps."""
    # Fixed interval: 50 lx
    levels = generate_isolux_levels(min_lux=180.0, max_lux=530.0, interval=50.0)
    assert 200.0 in levels
    assert 250.0 in levels
    assert 300.0 in levels
    assert 350.0 in levels
    assert 400.0 in levels
    assert 450.0 in levels
    assert 500.0 in levels
    assert np.all(np.diff(levels) == 50.0)

    # Automatic step calculation
    auto_levels = generate_isolux_levels(min_lux=300.0, max_lux=1200.0, interval=None)
    assert len(auto_levels) >= 3
    assert np.all(auto_levels >= 300.0)
    assert np.all(auto_levels <= 1200.0)
