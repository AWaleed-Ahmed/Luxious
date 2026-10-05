"""CSV Import and Export for Illuminance Measurements.

Supports standard CSV formats with optional metadata (device_name, timestamp, notes).
"""

from __future__ import annotations
import csv
import io
from typing import List, Tuple, Optional, Dict, Any

from models.project import LuminationProject
from models.measurement import MeasurementPoint


def export_measurements_to_csv(project: LuminationProject, file_path: str) -> None:
    """Export project measurement points to a CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["point", "x", "y", "lux", "expected_lux", "device", "timestamp", "notes"])
        for p in project.points:
            writer.writerow([
                p.id,
                f"{p.x:.4f}",
                f"{p.y:.4f}",
                f"{p.lux:.1f}" if p.lux is not None else "",
                f"{p.expected_lux:.1f}" if p.expected_lux is not None else "",
                p.device_name or "",
                p.timestamp or "",
                p.notes,
            ])


def import_measurements_from_csv(
    project: LuminationProject,
    file_path: str,
    create_missing_points: bool = True,
) -> Tuple[int, int]:
    """Import measurements from a CSV file into the project.

    Matches points by ID or by nearest (X, Y) coordinates.

    Returns:
        (updated_count, created_count)
    """
    updated_count = 0
    created_count = 0

    with open(file_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # Detect delimiter
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(content[:2048])
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ","

    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        return 0, 0

    header = [c.strip().lower() for c in rows[0]]

    # Determine column indexes
    id_col = -1
    x_col = -1
    y_col = -1
    lux_col = -1
    exp_col = -1
    dev_col = -1
    ts_col = -1
    notes_col = -1

    for idx, col in enumerate(header):
        if col in ("point", "id", "point_id", "name", "pt"):
            id_col = idx
        elif col in ("x", "x (m)", "x[m]", "pos_x"):
            x_col = idx
        elif col in ("y", "y (m)", "y[m]", "pos_y"):
            y_col = idx
        elif col in ("lux", "measured", "measured_lux", "illuminance", "e"):
            lux_col = idx
        elif col in ("expected", "expected_lux", "simulated", "dialux"):
            exp_col = idx
        elif col in ("device", "instrument", "device_name", "meter"):
            dev_col = idx
        elif col in ("timestamp", "time", "date"):
            ts_col = idx
        elif col in ("notes", "note", "comment"):
            notes_col = idx

    has_header = (x_col != -1 or y_col != -1 or lux_col != -1)
    data_rows = rows[1:] if has_header else rows

    # Fallback column order if no recognized header
    if not has_header:
        if len(data_rows[0]) >= 4:
            id_col, x_col, y_col, lux_col = 0, 1, 2, 3
        elif len(data_rows[0]) == 3:
            x_col, y_col, lux_col = 0, 1, 2

    for row in data_rows:
        if not row or all(c.strip() == "" for c in row):
            continue

        pt_id = row[id_col].strip() if id_col >= 0 and id_col < len(row) else None

        # Parse X, Y coordinates
        x_val: Optional[float] = None
        y_val: Optional[float] = None
        if x_col >= 0 and x_col < len(row) and row[x_col].strip():
            try:
                x_val = float(row[x_col].strip())
            except ValueError:
                pass
        if y_col >= 0 and y_col < len(row) and row[y_col].strip():
            try:
                y_val = float(row[y_col].strip())
            except ValueError:
                pass

        # Parse lux
        lux_val: Optional[float] = None
        if lux_col >= 0 and lux_col < len(row) and row[lux_col].strip():
            try:
                v = float(row[lux_col].strip())
                if v >= 0:
                    lux_val = v
            except ValueError:
                pass

        # Parse expected lux
        exp_val: Optional[float] = None
        if exp_col >= 0 and exp_col < len(row) and row[exp_col].strip():
            try:
                v = float(row[exp_col].strip())
                if v >= 0:
                    exp_val = v
            except ValueError:
                pass

        dev_val = row[dev_col].strip() if dev_col >= 0 and dev_col < len(row) else None
        ts_val = row[ts_col].strip() if ts_col >= 0 and ts_col < len(row) else None
        note_val = row[notes_col].strip() if notes_col >= 0 and notes_col < len(row) else ""

        # Match existing point by ID or coordinate
        target_pt: Optional[MeasurementPoint] = None
        if pt_id:
            target_pt = project.find_point_by_id(pt_id)

        if target_pt is None and x_val is not None and y_val is not None:
            # Find nearest point within 0.15m tolerance
            closest_dist = 0.15
            for p in project.points:
                d = ((p.x - x_val)**2 + (p.y - y_val)**2)**0.5
                if d < closest_dist:
                    closest_dist = d
                    target_pt = p

        if target_pt:
            if lux_val is not None:
                target_pt.record_reading(lux_val, timestamp=ts_val, device_name=dev_val)
            if exp_val is not None:
                target_pt.expected_lux = exp_val
            if note_val:
                target_pt.notes = note_val
            updated_count += 1
        elif create_missing_points and x_val is not None and y_val is not None:
            new_id = pt_id or f"P{len(project.points) + 1}"
            new_pt = MeasurementPoint(
                id=new_id,
                x=x_val,
                y=y_val,
                lux=lux_val,
                expected_lux=exp_val,
                device_name=dev_val,
                timestamp=ts_val,
                notes=note_val,
                locked_coordinates=False,
            )
            project.points.append(new_pt)
            created_count += 1

    if updated_count > 0 or created_count > 0:
        project.mark_modified()

    return updated_count, created_count
