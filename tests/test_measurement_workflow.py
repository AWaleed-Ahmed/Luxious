"""End-to-End Real Measurement Workflow Validation Tests.

Tests the full lifecycle:
Create room -> Generate grid -> Enter lux readings -> Calculate statistics ->
Interpolate -> Verify contours & heatmap -> Edit measurement -> Verify updates ->
Save project -> Reopen -> Confirm exact numerical & geometric fidelity.
"""

import os
import pytest
import numpy as np

from models.room import Room
from models.project import LuminationProject
from models.measurement import MeasurementPoint
from analysis.statistics import calculate_statistics
from analysis.interpolation import reconstruct_illuminance_field, _check_collinearity
from analysis.contours import generate_isolux_levels
from persistence.project_io import save_project, load_project


def test_complete_measurement_workflow(tmp_path):
    """Test full vertical workflow on a 6m x 4m room with 1m grid."""
    # 1. Create Room (6.0m x 4.0m, ceiling 2.8m, working plane 0.75m, margin 0.5m)
    room = Room(
        name="Survey Room 6x4",
        length=6.0,
        width=4.0,
        height=2.80,
        measurement_plane_height=0.75,
        wall_margin=0.50,
    )
    assert room.length == 6.0
    assert room.width == 4.0
    assert room.area == 24.0
    assert room.effective_length == 5.0  # 6.0 - 2*0.5
    assert room.effective_width == 3.0   # 4.0 - 2*0.5

    # 2. Generate Grid with ~1m spacing (5 cols along X, 3 rows along Y = 15 points)
    project = LuminationProject(name="6x4 Office Lighting Survey", room=room, target_lux=500.0)
    project.regenerate_grid(mode="count", rows=3, cols=5, wall_margin=0.50, centered_in_cells=True)

    assert len(project.points) == 15
    assert all(p.locked_coordinates for p in project.points)  # Grid coordinates locked by default

    # Verify all generated points are within the room
    for p in project.points:
        assert room.is_inside(p.x, p.y)

    # 3. Enter realistic physical lux measurements with bright center and darker perimeter
    # Row 1 (y ~ 1.0m): [310, 380, 420, 390, 320]
    # Row 2 (y ~ 2.0m): [370, 490, 580, 510, 380]
    # Row 3 (y ~ 3.0m): [330, 410, 460, 420, 340]
    lux_distribution = [
        310.0, 380.0, 420.0, 390.0, 320.0,
        370.0, 490.0, 580.0, 510.0, 380.0,
        330.0, 410.0, 460.0, 420.0, 340.0,
    ]
    for i, p in enumerate(project.points):
        p.record_reading(lux_distribution[i])

    # Store a copy of original measured values for immutability check
    original_lux_values = [p.lux for p in project.points]

    # 4. Calculate Statistics
    stats = calculate_statistics(project.points)
    assert stats is not None
    assert stats.count == 15
    assert stats.total_points == 15
    assert stats.e_min == 310.0
    assert stats.e_max == 580.0
    assert stats.min_point_id == "P1"
    assert stats.max_point_id == "P8"  # Center point (col 3, row 2)
    assert stats.min_coords == (project.points[0].x, project.points[0].y)
    assert stats.max_coords == (project.points[7].x, project.points[7].y)

    expected_avg = float(np.mean(lux_distribution))
    assert pytest.approx(stats.e_avg, 0.01) == expected_avg
    assert pytest.approx(stats.uniformity_u0, 0.001) == 310.0 / expected_avg
    assert pytest.approx(stats.median, 0.01) == float(np.median(lux_distribution))
    assert pytest.approx(stats.std_dev, 0.01) == float(np.std(lux_distribution, ddof=1))
    assert stats.range_val == 580.0 - 310.0

    # 5. Perform 2D Scientific Interpolation
    interp = reconstruct_illuminance_field(
        points=project.points,
        room=room,
        resolution=100,
        method="linear",
        extrapolate_to_walls=False,
    )
    assert interp.success is True
    assert interp.method_used == "linear"
    assert interp.is_fallback is False
    assert interp.num_points_used == 15

    # VERIFY POINT 1: Original measured lux values are NEVER modified by interpolation
    for i, p in enumerate(project.points):
        assert p.lux == original_lux_values[i]

    # VERIFY POINT 6: Heatmap and Contours use the exact same grid_z
    valid_z = interp.grid_z[~np.isnan(interp.grid_z)]
    assert len(valid_z) > 0
    vmin = float(np.min(valid_z))
    vmax = float(np.max(valid_z))
    assert 310.0 <= vmin <= 325.0
    assert 570.0 <= vmax <= 580.0

    # 6. Generate Isolux Contours from the interpolated field
    levels = generate_isolux_levels(vmin, vmax, interval=50.0)
    assert 350.0 in levels
    assert 400.0 in levels
    assert 450.0 in levels
    assert 500.0 in levels
    assert 550.0 in levels

    # 7. Edit a measurement (e.g. point P8 from 580 lx to 650 lx)
    p8 = project.find_point_by_id("P8")
    assert p8 is not None
    p8.record_reading(650.0)

    # 8. Re-calculate statistics and verify affected results update correctly
    new_stats = calculate_statistics(project.points)
    assert new_stats is not None
    assert new_stats.e_max == 650.0
    assert new_stats.max_point_id == "P8"
    assert new_stats.range_val == 650.0 - 310.0
    assert new_stats.e_avg > stats.e_avg

    # Re-interpolate with modified measurement
    new_interp = reconstruct_illuminance_field(project.points, room, resolution=100, method="linear")
    new_valid_z = new_interp.grid_z[~np.isnan(new_interp.grid_z)]
    assert 640.0 <= float(np.max(new_valid_z)) <= 650.0

    # 9. Save project to disk (.luxproj)
    save_path = str(tmp_path / "office_6x4_test.luxproj")
    save_project(project, save_path)
    assert os.path.exists(save_path)

    # 10. Reopen project and verify exact data & result identity
    reopened = load_project(save_path)
    assert reopened.name == "6x4 Office Lighting Survey"
    assert reopened.target_lux == 500.0
    assert reopened.room.length == 6.0
    assert reopened.room.width == 4.0
    assert reopened.room.height == 2.80
    assert reopened.room.measurement_plane_height == 0.75
    assert reopened.room.wall_margin == 0.50
    assert len(reopened.points) == 15

    # Check every point coordinate and lux value matches exactly
    for i, orig_pt in enumerate(project.points):
        reopened_pt = reopened.points[i]
        assert reopened_pt.id == orig_pt.id
        assert pytest.approx(reopened_pt.x, 1e-4) == orig_pt.x
        assert pytest.approx(reopened_pt.y, 1e-4) == orig_pt.y
        assert reopened_pt.lux == orig_pt.lux
        assert reopened_pt.locked_coordinates == orig_pt.locked_coordinates

    # Re-run statistics on reopened project -> must match new_stats exactly
    reopened_stats = calculate_statistics(reopened.points)
    assert reopened_stats is not None
    assert reopened_stats.e_avg == new_stats.e_avg
    assert reopened_stats.e_min == new_stats.e_min
    assert reopened_stats.e_max == new_stats.e_max
    assert reopened_stats.uniformity_u0 == new_stats.uniformity_u0


def test_missing_unmeasured_points_not_zero():
    """Verify that unmeasured grid points are completely ignored in stats and NOT treated as 0 lux."""
    points = [
        MeasurementPoint(id="P1", x=1.0, y=1.0, lux=400.0),
        MeasurementPoint(id="P2", x=2.0, y=1.0, lux=600.0),
        MeasurementPoint(id="P3", x=1.0, y=2.0, lux=None),  # Unmeasured
        MeasurementPoint(id="P4", x=2.0, y=2.0, lux=None),  # Unmeasured
    ]

    stats = calculate_statistics(points)
    assert stats is not None
    assert stats.count == 2
    assert stats.total_points == 4
    # If unmeasured were treated as 0, avg would be (400+600+0+0)/4 = 250 and min would be 0
    # Correct avg is (400+600)/2 = 500 and min is 400
    assert stats.e_avg == 500.0
    assert stats.e_min == 400.0
    assert stats.e_max == 600.0
    assert stats.uniformity_u0 == 400.0 / 500.0  # 0.80, NOT 0.0


def test_geometrically_invalid_collinear_points():
    """Verify that 3 or more points on a single line are detected as collinear and fail gracefully."""
    room = Room(length=6.0, width=4.0)
    # 5 points all placed along y = 1.5
    points = [
        MeasurementPoint(id="P1", x=1.0, y=1.5, lux=300.0),
        MeasurementPoint(id="P2", x=2.0, y=1.5, lux=350.0),
        MeasurementPoint(id="P3", x=3.0, y=1.5, lux=400.0),
        MeasurementPoint(id="P4", x=4.0, y=1.5, lux=450.0),
        MeasurementPoint(id="P5", x=5.0, y=1.5, lux=500.0),
    ]

    # Check collinearity detector
    xy = np.array([[p.x, p.y] for p in points])
    assert _check_collinearity(xy) is True

    # Reconstruct field should NOT crash, but report fallback with explicit messaging
    res = reconstruct_illuminance_field(points, room, method="linear")
    assert res.success is False
    assert res.is_fallback is True
    assert "A 2D illuminance field cannot be reconstructed from the current measurement geometry" in res.fallback_reason
