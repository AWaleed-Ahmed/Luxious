"""Unit tests for Target Comparison and DIALux Simulated Comparison."""

import pytest
from models.measurement import MeasurementPoint
from analysis.comparison import compare_with_target, compare_measured_with_simulated


def test_target_comparison():
    """Verify target comparison calculations without false legal claims."""
    points = [
        MeasurementPoint(id="P1", x=0.5, y=0.5, lux=300.0),
        MeasurementPoint(id="P2", x=1.5, y=0.5, lux=450.0),
        MeasurementPoint(id="P3", x=2.5, y=0.5, lux=500.0),
        MeasurementPoint(id="P4", x=0.5, y=1.5, lux=550.0),
    ]

    target = 500.0
    res = compare_with_target(points, target)
    assert res is not None
    assert res.target_lux == 500.0
    assert res.points_evaluated == 4
    assert res.points_below_target == 2  # 300 and 450
    assert res.percentage_below_target == 50.0
    assert res.points_above_or_equal_target == 2  # 500 and 550
    assert res.percentage_above_or_equal == 50.0

    # Max deficit is from P1 (300 lx -> 200 deficit)
    assert res.max_negative_deficit == 200.0
    assert res.max_deficit_point_id == "P1"

    # Verify standard notice format
    assert "Target entered by user: 500 lx" in res.summary_text
    assert "2 of 4 measurement points are below the selected target" in res.summary_text


def test_simulated_dialux_comparison():
    """Verify Delta E and percentage difference calculations between measured and expected."""
    points = [
        MeasurementPoint(id="P1", x=1.0, y=1.0, lux=400.0, expected_lux=500.0),
        MeasurementPoint(id="P2", x=2.0, y=1.0, lux=600.0, expected_lux=500.0),
    ]

    res = compare_measured_with_simulated(points)
    assert res is not None
    assert res.points_evaluated == 2
    # P1 delta: 400 - 500 = -100 (20% diff)
    # P2 delta: 600 - 500 = +100 (20% diff)
    assert res.mean_delta == 0.0
    assert res.mean_absolute_error == 100.0
    assert res.root_mean_squared_error == 100.0
    assert res.mean_percentage_diff == 20.0
