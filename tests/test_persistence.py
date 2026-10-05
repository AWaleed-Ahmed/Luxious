"""Unit tests for Persistence (JSON Project I/O and CSV I/O) and PDF Reporting."""

import os
import tempfile
import pytest

from models.room import Room
from models.project import LuminationProject
from models.measurement import MeasurementPoint
from persistence.project_io import save_project, load_project
from persistence.csv_io import export_measurements_to_csv, import_measurements_from_csv
from reporting.pdf_report import generate_pdf_report
from reporting.chart_exporter import export_room_map_image


def test_project_json_save_and_load(tmp_path):
    """Verify full fidelity roundtrip saving and loading of project JSON."""
    file_path = str(tmp_path / "test_room.luxproj")

    room = Room(
        name="Conference Room",
        length=8.0,
        width=5.0,
        height=3.0,
        measurement_plane_height=0.85,
        wall_margin=0.6,
    )
    project = LuminationProject(
        name="Conference Room Survey",
        author="John Doe",
        room=room,
        target_lux=400.0,
    )
    project.regenerate_grid(rows=3, cols=4)
    project.points[0].record_reading(350.0)
    project.points[0].expected_lux = 400.0
    project.points[1].record_reading(420.0)

    # Save
    save_project(project, file_path)
    assert os.path.exists(file_path)

    # Load
    loaded = load_project(file_path)
    assert loaded.name == "Conference Room Survey"
    assert loaded.author == "John Doe"
    assert loaded.target_lux == 400.0
    assert loaded.room.length == 8.0
    assert loaded.room.width == 5.0
    assert loaded.room.height == 3.0
    assert loaded.room.measurement_plane_height == 0.85
    assert len(loaded.points) == 12
    assert loaded.points[0].lux == 350.0
    assert loaded.points[0].expected_lux == 400.0
    assert loaded.points[1].lux == 420.0


def test_csv_export_and_import(tmp_path):
    """Verify CSV export and import roundtrip."""
    file_path = str(tmp_path / "measurements.csv")

    room = Room(length=6.0, width=4.0)
    project = LuminationProject(name="Test CSV", room=room)
    project.regenerate_grid(rows=2, cols=2)
    project.points[0].record_reading(312.0)
    project.points[1].record_reading(347.0)
    project.points[2].record_reading(405.0)

    # Export
    export_measurements_to_csv(project, file_path)
    assert os.path.exists(file_path)

    # Create fresh empty project with same room grid
    new_project = LuminationProject(name="Imported", room=Room(length=6.0, width=4.0))
    new_project.regenerate_grid(rows=2, cols=2)

    # Import
    updated, created = import_measurements_from_csv(new_project, file_path)
    assert updated == 4
    assert new_project.points[0].lux == 312.0
    assert new_project.points[1].lux == 347.0
    assert new_project.points[2].lux == 405.0


def test_pdf_report_and_map_export(tmp_path):
    """Verify PDF report and high-res map image generation execute without error."""
    pdf_path = str(tmp_path / "survey_report.pdf")
    img_path = str(tmp_path / "map.png")

    room = Room(length=6.0, width=4.0)
    project = LuminationProject(name="PDF Test Survey", room=room, target_lux=500.0)
    project.regenerate_grid(rows=3, cols=3)
    for i, p in enumerate(project.points):
        p.record_reading(300.0 + i * 40.0)
        p.expected_lux = 450.0

    # Test PDF generation
    out_pdf = generate_pdf_report(project, pdf_path)
    assert os.path.exists(out_pdf)
    assert os.path.getsize(out_pdf) > 1000  # Non-trivial PDF file

    # Test Map Image generation
    img_bytes = export_room_map_image(project, output_path=img_path, dpi=150)
    assert os.path.exists(img_path)
    assert len(img_bytes) > 1000
