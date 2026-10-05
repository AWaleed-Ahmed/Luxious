"""Professional PDF Report Generator.

Creates comprehensive engineering reports for illuminance surveys using ReportLab.
Includes metadata, KPI tables, high-resolution false-colour maps, isolux contours,
target comparison, simulated DIALux analysis, and scientific methodology notices.
"""

from __future__ import annotations
import os
import io
from datetime import datetime
from typing import Optional, List, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)

from models.project import LuminationProject
from analysis.statistics import calculate_statistics
from analysis.comparison import compare_with_target, compare_measured_with_simulated
from reporting.chart_exporter import export_room_map_image, export_charts_image


def generate_pdf_report(
    project: LuminationProject,
    output_path: str,
) -> str:
    """Generate a multi-page professional PDF illuminance survey report."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e3a8a"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    bold_body_style = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName="Helvetica-Bold",
    )

    methodology_style = ParagraphStyle(
        "Methodology",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569"),
        fontName="Helvetica-Oblique",
    )

    story: List[Any] = []

    # 1. Header Banner
    story.append(Paragraph("LUMINATION — REAL-ROOM ILLUMINANCE SURVEY REPORT", subtitle_style))
    story.append(Paragraph(project.name or "Illuminance Survey Report", title_style))

    cur_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    meta_text = (
        f"<b>Survey Date:</b> {cur_time} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Surveyor/Author:</b> {project.author or 'Not specified'} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Room:</b> {project.room.name}"
    )
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=10))

    # 2. Room Geometry & Survey Parameters
    room = project.room
    geom_data = [
        [
            Paragraph("<b>Room Dimensions:</b>", body_style),
            Paragraph(f"{room.length:.2f} m (L) × {room.width:.2f} m (W)", body_style),
            Paragraph("<b>Floor Area:</b>", body_style),
            Paragraph(f"{room.area:.2f} m²", body_style),
        ],
        [
            Paragraph("<b>Ceiling Height:</b>", body_style),
            Paragraph(f"{room.height:.2f} m", body_style),
            Paragraph("<b>Working Plane Height:</b>", body_style),
            Paragraph(f"{room.measurement_plane_height:.2f} m", body_style),
        ],
        [
            Paragraph("<b>Wall Margin Band:</b>", body_style),
            Paragraph(f"{room.wall_margin:.2f} m", body_style),
            Paragraph("<b>Grid Points Total:</b>", body_style),
            Paragraph(f"{len(project.points)} points ({len(project.get_measured_points())} measured)", body_style),
        ],
    ]
    geom_table = Table(geom_data, colWidths=[3.5 * cm, 5.0 * cm, 4.0 * cm, 4.5 * cm])
    geom_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(geom_table)
    story.append(Spacer(1, 10))

    # 3. Numerical Statistics / Photometric KPI Summary
    stats = calculate_statistics(project.points)
    story.append(Paragraph("Photometric Numerical Analysis", section_heading))

    if stats:
        min_loc = f"({stats.min_coords[0]:.2f}, {stats.min_coords[1]:.2f}) m" if stats.min_coords else "-"
        max_loc = f"({stats.max_coords[0]:.2f}, {stats.max_coords[1]:.2f}) m" if stats.max_coords else "-"

        kpi_data = [
            [
                Paragraph("<b>Average Illuminance (E<sub>avg</sub>)</b>", bold_body_style),
                Paragraph(f"<b>{stats.e_avg:.1f} lx</b>", bold_body_style),
                Paragraph("<b>Uniformity U<sub>0</sub> (E<sub>min</sub> / E<sub>avg</sub>)</b>", bold_body_style),
                Paragraph(f"<b>{stats.uniformity_u0:.3f}</b>", bold_body_style),
            ],
            [
                Paragraph("<b>Minimum Illuminance (E<sub>min</sub>)</b>", body_style),
                Paragraph(f"{stats.e_min:.1f} lx &nbsp; <font color='#64748b'>at {stats.min_point_id or ''} {min_loc}</font>", body_style),
                Paragraph("<b>Uniformity U<sub>1</sub> (E<sub>min</sub> / E<sub>max</sub>)</b>", body_style),
                Paragraph(f"{stats.uniformity_u1:.3f}", body_style),
            ],
            [
                Paragraph("<b>Maximum Illuminance (E<sub>max</sub>)</b>", body_style),
                Paragraph(f"{stats.e_max:.1f} lx &nbsp; <font color='#64748b'>at {stats.max_point_id or ''} {max_loc}</font>", body_style),
                Paragraph("<b>Standard Deviation (σ)</b>", body_style),
                Paragraph(f"{stats.std_dev:.1f} lx", body_style),
            ],
            [
                Paragraph("<b>Range (E<sub>max</sub> − E<sub>min</sub>)</b>", body_style),
                Paragraph(f"{stats.range_val:.1f} lx", body_style),
                Paragraph("<b>Median Illuminance</b>", body_style),
                Paragraph(f"{stats.median:.1f} lx", body_style),
            ],
        ]
        kpi_table = Table(kpi_data, colWidths=[5.5 * cm, 4.5 * cm, 4.5 * cm, 2.5 * cm])
        kpi_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eff6ff")),
                ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#93c5fd")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        story.append(kpi_table)
    else:
        story.append(Paragraph("<i>No measured readings available for statistical calculation.</i>", body_style))

    story.append(Spacer(1, 10))

    # 4. Target Comparison (if applicable)
    if project.target_lux and project.target_lux > 0:
        target_comp = compare_with_target(project.points, project.target_lux)
        if target_comp:
            story.append(Paragraph("Comparison with Selected Target Illuminance", section_heading))
            tgt_text = (
                f"<b>Target Reference:</b> {target_comp.target_lux:.0f} lx &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Points Evaluated:</b> {target_comp.points_evaluated} &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Points Below Target:</b> {target_comp.points_below_target} ({target_comp.percentage_below_target:.1f}%) &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Points ≥ Target:</b> {target_comp.points_above_or_equal_target} ({target_comp.percentage_above_or_equal:.1f}%) &nbsp;&nbsp;|&nbsp;&nbsp; "
                f"<b>Mean Abs Deviation:</b> {target_comp.avg_absolute_deviation:.1f} lx"
            )
            story.append(Paragraph(tgt_text, body_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<i>Notice: {target_comp.summary_text}</i>", body_style))
            story.append(Spacer(1, 8))

    # 5. 2D Illuminance Map & Isolux Diagram
    story.append(Paragraph("2D Illuminance Distribution Map & Isolux Contours", section_heading))

    map_img_bytes = export_room_map_image(project, dpi=200, width_in=7.0, height_in=4.6)
    map_buf = io.BytesIO(map_img_bytes)
    story.append(RLImage(map_buf, width=17.0 * cm, height=11.2 * cm))
    story.append(Spacer(1, 6))

    # Scientific Methodology Notice
    methodology_note = (
        "<b>Scientific Methodology Note:</b> The continuous false-colour map and isolux contour lines represent "
        "numerical spatial estimates reconstructed between physical measurement locations. Physical measurement markers (points) "
        "represent actual readings recorded at the working plane with a physical lux meter. Interpolated values between points "
        "are mathematical estimates and are not presented as direct measurements."
    )
    story.append(Paragraph(methodology_note, methodology_style))
    story.append(Spacer(1, 10))

    # 6. Distribution Charts
    story.append(Paragraph("Illuminance Frequency Distribution & Compliance", section_heading))
    chart_img_bytes = export_charts_image(project, dpi=200)
    chart_buf = io.BytesIO(chart_img_bytes)
    story.append(RLImage(chart_buf, width=17.0 * cm, height=6.4 * cm))
    story.append(Spacer(1, 12))

    # 7. Measurement Schedule Table
    story.append(Paragraph("Measurement Schedule & Location Coordinates", section_heading))

    table_rows = [
        [
            Paragraph("<b>Point ID</b>", bold_body_style),
            Paragraph("<b>X (m)</b>", bold_body_style),
            Paragraph("<b>Y (m)</b>", bold_body_style),
            Paragraph("<b>Measured Lux</b>", bold_body_style),
            Paragraph("<b>Expected Lux</b>", bold_body_style),
            Paragraph("<b>Δ E (lx)</b>", bold_body_style),
            Paragraph("<b>Notes / Instrument</b>", bold_body_style),
        ]
    ]

    for p in project.points:
        meas_str = f"{p.lux:.1f}" if p.lux is not None else "-"
        exp_str = f"{p.expected_lux:.1f}" if p.expected_lux is not None else "-"
        delta_str = f"{p.delta_lux:+.1f}" if p.delta_lux is not None else "-"

        notes_combined = p.notes
        if p.device_name:
            notes_combined = f"[{p.device_name}] " + notes_combined if notes_combined else f"[{p.device_name}]"
        if p.is_possible_outlier:
            notes_combined = "⚠ " + notes_combined

        table_rows.append([
            Paragraph(p.id, body_style),
            Paragraph(f"{p.x:.2f}", body_style),
            Paragraph(f"{p.y:.2f}", body_style),
            Paragraph(meas_str, body_style),
            Paragraph(exp_str, body_style),
            Paragraph(delta_str, body_style),
            Paragraph(notes_combined or "", body_style),
        ])

    sched_table = Table(
        table_rows,
        colWidths=[2.0 * cm, 2.0 * cm, 2.0 * cm, 2.8 * cm, 2.8 * cm, 2.4 * cm, 3.0 * cm],
    )
    sched_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )
    story.append(sched_table)

    # Build PDF document
    doc.build(story)
    return output_path
