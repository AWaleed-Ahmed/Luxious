"""Offscreen Chart & Map Exporter.

Renders high-resolution raster (PNG) or vector (SVG/PDF) images of the room plan,
false-colour heatmap, and isolux contours for reports and standalone export.
"""

from __future__ import annotations
import io
import os
from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from models.project import LuminationProject, VisualizationSettings
from analysis.interpolation import InterpolationResult, reconstruct_illuminance_field
from analysis.comparison import TargetComparisonResult, compare_with_target
from visualization.map_plotter import render_room_map
from visualization.chart_plotter import render_distribution_histogram, render_target_compliance_bar


def export_room_map_image(
    project: LuminationProject,
    interp_result: Optional[InterpolationResult] = None,
    output_path: Optional[str] = None,
    dpi: int = 300,
    width_in: float = 8.0,
    height_in: float = 6.0,
    override_settings: Optional[VisualizationSettings] = None,
) -> bytes:
    """Render and export the room illuminance map to a byte buffer or image file."""
    fig, ax = plt.subplots(figsize=(width_in, height_in), dpi=dpi)
    fig.patch.set_facecolor("#ffffff")

    render_room_map(
        ax=ax,
        project=project,
        interp_result=interp_result,
        override_settings=override_settings,
        highlight_min_max=True,
    )

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    img_data = buf.getvalue()
    buf.close()

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(img_data)

    return img_data


def export_charts_image(
    project: LuminationProject,
    output_path: Optional[str] = None,
    dpi: int = 300,
) -> bytes:
    """Render analytical distribution and target compliance charts into an image."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.2), dpi=dpi)
    fig.patch.set_facecolor("#ffffff")

    render_distribution_histogram(ax1, project.points, target_lux=project.target_lux)

    if project.target_lux and project.target_lux > 0:
        comp = compare_with_target(project.points, project.target_lux)
        if comp:
            render_target_compliance_bar(ax2, comp)
        else:
            ax2.axis("off")
    else:
        ax2.axis("off")

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)

    img_data = buf.getvalue()
    buf.close()

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(img_data)

    return img_data
