"""Analysis package for Lumination."""

from analysis.statistics import calculate_statistics, calculate_matrix_statistics, StatisticalSummary
from analysis.interpolation import reconstruct_illuminance_field, InterpolationResult
from analysis.contours import generate_isolux_levels
from analysis.comparison import (
    compare_with_target,
    compare_measured_with_simulated,
    TargetComparisonResult,
    SimulatedComparisonResult,
    PointDelta,
)

__all__ = [
    "calculate_statistics",
    "calculate_matrix_statistics",
    "StatisticalSummary",
    "reconstruct_illuminance_field",
    "InterpolationResult",
    "generate_isolux_levels",
    "compare_with_target",
    "compare_measured_with_simulated",
    "TargetComparisonResult",
    "SimulatedComparisonResult",
    "PointDelta",
]
