"""Unit tests for Photometric Numerical Statistics calculations."""

import pytest
import numpy as np

from models.measurement import MeasurementPoint
from analysis.statistics import calculate_statistics, calculate_matrix_statistics


def test_reference_matrix_statistics():
    """Verify statistics on the reference test matrix specified in the requirements:

    [300, 400, 500]
    [400, 500, 600]
    [500, 600, 700]

    Expected:
    - Minimum = 300
    - Maximum = 700
    - Average = 500
    - Uniformity U0 = 300 / 500 = 0.60
    - Median = 500
    - Range = 400
    """
    matrix = np.array([
        [300, 400, 500],
        [400, 500, 600],
        [500, 600, 700],
    ])

    stats = calculate_matrix_statistics(matrix)
    assert stats is not None
    assert stats.e_min == 300.0
    assert stats.e_max == 700.0
    assert stats.e_avg == 500.0
    assert pytest.approx(stats.uniformity_u0, 0.001) == 0.60
    assert pytest.approx(stats.uniformity_u1, 0.001) == 300.0 / 700.0
    assert stats.median == 500.0
    assert stats.range_val == 400.0
    assert stats.count == 9


def test_points_statistics_and_coordinates():
    """Verify statistics calculation from MeasurementPoint list including coordinate tracking."""
    points = [
        MeasurementPoint(id="P1", x=0.5, y=0.5, lux=320.0),
        MeasurementPoint(id="P2", x=1.5, y=0.5, lux=370.0),
        MeasurementPoint(id="P3", x=2.5, y=0.5, lux=410.0),
        MeasurementPoint(id="P4", x=0.5, y=1.5, lux=380.0),
        MeasurementPoint(id="P5", x=1.5, y=1.5, lux=450.0),
        MeasurementPoint(id="P6", x=2.5, y=1.5, lux=520.0),
        MeasurementPoint(id="P7", x=0.5, y=2.5, lux=None),  # Unmeasured point should be ignored
    ]

    stats = calculate_statistics(points)
    assert stats is not None
    assert stats.count == 6
    assert stats.total_points == 7
    assert stats.e_min == 320.0
    assert stats.min_point_id == "P1"
    assert stats.min_coords == (0.5, 0.5)

    assert stats.e_max == 520.0
    assert stats.max_point_id == "P6"
    assert stats.max_coords == (2.5, 1.5)

    expected_avg = (320 + 370 + 410 + 380 + 450 + 520) / 6.0
    assert pytest.approx(stats.e_avg, 0.01) == expected_avg
    assert pytest.approx(stats.uniformity_u0, 0.001) == 320.0 / expected_avg


def test_edge_cases_statistics():
    """Verify graceful handling of empty, single point, and zero datasets."""
    # Empty
    assert calculate_statistics([]) is None

    # Only unmeasured points
    unmeasured = [MeasurementPoint(id="P1", x=1.0, y=1.0, lux=None)]
    assert calculate_statistics(unmeasured) is None

    # Single point
    single = [MeasurementPoint(id="P1", x=1.0, y=1.0, lux=450.0)]
    stats_single = calculate_statistics(single)
    assert stats_single is not None
    assert stats_single.count == 1
    assert stats_single.e_avg == 450.0
    assert stats_single.uniformity_u0 == 1.0
    assert stats_single.std_dev == 0.0
