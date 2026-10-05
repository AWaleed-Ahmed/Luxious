"""Unit tests for 2D Spatial Interpolation and Edge Cases."""

import pytest
import numpy as np

from models.room import Room
from models.measurement import MeasurementPoint
from analysis.interpolation import reconstruct_illuminance_field


def test_linear_interpolation_default():
    """Verify default linear 2D interpolation produces valid bounded values."""
    room = Room(length=4.0, width=4.0)
    # 4 corner points with known gradient
    points = [
        MeasurementPoint(id="P1", x=1.0, y=1.0, lux=200.0),
        MeasurementPoint(id="P2", x=3.0, y=1.0, lux=400.0),
        MeasurementPoint(id="P3", x=1.0, y=3.0, lux=400.0),
        MeasurementPoint(id="P4", x=3.0, y=3.0, lux=600.0),
    ]

    res = reconstruct_illuminance_field(points, room, resolution=50, method="linear")
    assert res.success is True
    assert res.method_used == "linear"
    assert res.is_fallback is False
    assert res.num_points_used == 4

    # The center point (2.0, 2.0) should interpolate to ~400 lux
    # Find grid coordinate closest to (2.0, 2.0)
    dist_sq = (res.grid_x - 2.0) ** 2 + (res.grid_y - 2.0) ** 2
    center_idx = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)
    interpolated_center = res.grid_z[center_idx]
    assert pytest.approx(interpolated_center, abs=15.0) == 400.0

    # Outside the convex hull (e.g. at (0.1, 0.1)), value must be NaN when extrapolate_to_walls=False
    dist_sq_corner = (res.grid_x - 0.1) ** 2 + (res.grid_y - 0.1) ** 2
    corner_idx = np.unravel_index(np.argmin(dist_sq_corner), dist_sq_corner.shape)
    assert np.isnan(res.grid_z[corner_idx])


def test_interpolation_optional_methods():
    """Verify cubic, rbf, and nearest methods on sufficient data."""
    room = Room(length=5.0, width=5.0)
    # 3x3 grid (9 points)
    points = []
    idx = 1
    for y in [1.0, 2.5, 4.0]:
        for x in [1.0, 2.5, 4.0]:
            points.append(MeasurementPoint(id=f"P{idx}", x=x, y=y, lux=300.0 + x * 50 + y * 40))
            idx += 1

    # Cubic
    res_cubic = reconstruct_illuminance_field(points, room, method="cubic")
    assert res_cubic.success is True
    assert res_cubic.method_used == "cubic"

    # RBF
    res_rbf = reconstruct_illuminance_field(points, room, method="rbf")
    assert res_rbf.success is True
    assert res_rbf.method_used == "rbf"

    # Nearest
    res_nearest = reconstruct_illuminance_field(points, room, method="nearest")
    assert res_nearest.success is True
    assert res_nearest.method_used == "nearest"


def test_collinear_points_fallback():
    """Verify collinear points detect collinearity and fallback gracefully without crashing."""
    room = Room(length=6.0, width=4.0)
    # All points lie along Y = 2.0
    points = [
        MeasurementPoint(id="P1", x=1.0, y=2.0, lux=300.0),
        MeasurementPoint(id="P2", x=2.0, y=2.0, lux=400.0),
        MeasurementPoint(id="P3", x=3.0, y=2.0, lux=500.0),
        MeasurementPoint(id="P4", x=4.0, y=2.0, lux=600.0),
    ]

    res = reconstruct_illuminance_field(points, room, method="linear")
    assert res.success is False
    assert res.is_fallback is True
    assert "A 2D illuminance field cannot be reconstructed from the current measurement geometry" in res.fallback_reason


def test_sparse_data_fallback():
    """Verify sparse data (< 3 points) is handled gracefully with informative fallback notice."""
    room = Room(length=4.0, width=4.0)
    # 2 points
    points = [
        MeasurementPoint(id="P1", x=1.0, y=1.0, lux=300.0),
        MeasurementPoint(id="P2", x=3.0, y=3.0, lux=500.0),
    ]
    res = reconstruct_illuminance_field(points, room, method="linear")
    assert res.success is True
    assert res.is_fallback is True
    assert "2 measurement points" in res.fallback_reason
