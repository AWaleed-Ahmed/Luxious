"""Numerical Statistics Analysis for Illuminance Data.

Computes standard lighting engineering metrics:
- E_avg (Average illuminance)
- E_min (Minimum illuminance) and coordinates
- E_max (Maximum illuminance) and coordinates
- U0 (Uniformity: E_min / E_avg)
- U1 (Uniformity: E_min / E_max)
- Standard deviation
- Median
- Range (E_max - E_min)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple, Sequence, Dict, Any
import numpy as np

from models.measurement import MeasurementPoint


@dataclass
class StatisticalSummary:
    """Numerical summary of physical illuminance measurements."""
    count: int
    total_points: int
    e_avg: float
    e_min: float
    e_max: float
    min_coords: Optional[Tuple[float, float]]
    max_coords: Optional[Tuple[float, float]]
    min_point_id: Optional[str]
    max_point_id: Optional[str]
    uniformity_u0: float
    uniformity_u1: float
    std_dev: float
    median: float
    range_val: float
    variance: float
    coefficient_of_variation: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "total_points": self.total_points,
            "e_avg": round(self.e_avg, 2),
            "e_min": round(self.e_min, 2),
            "e_max": round(self.e_max, 2),
            "min_coords": self.min_coords,
            "max_coords": self.max_coords,
            "min_point_id": self.min_point_id,
            "max_point_id": self.max_point_id,
            "uniformity_u0": round(self.uniformity_u0, 3),
            "uniformity_u1": round(self.uniformity_u1, 3),
            "std_dev": round(self.std_dev, 2),
            "median": round(self.median, 2),
            "range_val": round(self.range_val, 2),
            "variance": round(self.variance, 2),
            "coefficient_of_variation": round(self.coefficient_of_variation, 3),
        }


def calculate_statistics(points: Sequence[MeasurementPoint]) -> Optional[StatisticalSummary]:
    """Calculate standard lighting statistics from a sequence of MeasurementPoints.

    Ignores unmeasured points (lux is None).

    Returns:
        StatisticalSummary object, or None if no valid measured points exist.
    """
    total_count = len(points)
    measured = [p for p in points if p.is_measured and p.lux is not None and p.lux >= 0]

    if not measured:
        return None

    lux_values = np.array([p.lux for p in measured], dtype=np.float64)
    n = len(lux_values)

    e_avg = float(np.mean(lux_values))
    e_min = float(np.min(lux_values))
    e_max = float(np.max(lux_values))

    min_idx = int(np.argmin(lux_values))
    max_idx = int(np.argmax(lux_values))

    min_pt = measured[min_idx]
    max_pt = measured[max_idx]

    min_coords = (min_pt.x, min_pt.y)
    max_coords = (max_pt.x, max_pt.y)
    min_point_id = min_pt.id
    max_point_id = max_pt.id

    uniformity_u0 = (e_min / e_avg) if e_avg > 0 else 0.0
    uniformity_u1 = (e_min / e_max) if e_max > 0 else 0.0

    std_dev = float(np.std(lux_values, ddof=1)) if n > 1 else 0.0
    variance = float(np.var(lux_values, ddof=1)) if n > 1 else 0.0
    median = float(np.median(lux_values))
    range_val = e_max - e_min
    cv = (std_dev / e_avg) if e_avg > 0 else 0.0

    return StatisticalSummary(
        count=n,
        total_points=total_count,
        e_avg=e_avg,
        e_min=e_min,
        e_max=e_max,
        min_coords=min_coords,
        max_coords=max_coords,
        min_point_id=min_point_id,
        max_point_id=max_point_id,
        uniformity_u0=uniformity_u0,
        uniformity_u1=uniformity_u1,
        std_dev=std_dev,
        median=median,
        range_val=range_val,
        variance=variance,
        coefficient_of_variation=cv,
    )


def calculate_matrix_statistics(matrix: np.ndarray) -> Optional[StatisticalSummary]:
    """Calculate statistics directly from a 2D or 1D numerical NumPy array of lux values.

    Handles NaN values gracefully by filtering them out.
    """
    arr = np.asarray(matrix, dtype=np.float64).flatten()
    valid = arr[~np.isnan(arr) & (arr >= 0)]

    if len(valid) == 0:
        return None

    n = len(valid)
    e_avg = float(np.mean(valid))
    e_min = float(np.min(valid))
    e_max = float(np.max(valid))

    uniformity_u0 = (e_min / e_avg) if e_avg > 0 else 0.0
    uniformity_u1 = (e_min / e_max) if e_max > 0 else 0.0

    std_dev = float(np.std(valid, ddof=1)) if n > 1 else 0.0
    variance = float(np.var(valid, ddof=1)) if n > 1 else 0.0
    median = float(np.median(valid))
    range_val = e_max - e_min
    cv = (std_dev / e_avg) if e_avg > 0 else 0.0

    return StatisticalSummary(
        count=n,
        total_points=len(arr),
        e_avg=e_avg,
        e_min=e_min,
        e_max=e_max,
        min_coords=None,
        max_coords=None,
        min_point_id=None,
        max_point_id=None,
        uniformity_u0=uniformity_u0,
        uniformity_u1=uniformity_u1,
        std_dev=std_dev,
        median=median,
        range_val=range_val,
        variance=variance,
        coefficient_of_variation=cv,
    )
