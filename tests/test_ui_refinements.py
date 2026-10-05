"""Tests for UI Refinements, i18n, Undo/Redo, and Symmetry Snapping."""

import pytest
import math
from models.room import Room
from models.project import LuminationProject
from models.measurement import MeasurementPoint
from utils.undo_commands import (
    SetMeasurementLuxCommand,
    AddPointCommand,
    DeletePointCommand,
)
from i18n.translations import TranslationManager, tr


def test_i18n_translation_switching():
    """Verify that language manager translates strings to English, Romanian, and German."""
    tm = TranslationManager.get_instance()

    # English
    tm.set_language("en")
    assert tr("menu_file") == "File"
    assert tr("action_add_custom") == "Add Custom Point"
    assert tr("canvas_x_axis") == "X (meters)"

    # Romanian
    tm.set_language("ro")
    assert tr("menu_file") == "Fișier"
    assert tr("action_add_custom") == "Adaugă punct personalizat"
    assert tr("canvas_x_axis") == "X (metri)"

    # German
    tm.set_language("de")
    assert tr("menu_file") == "Datei"
    assert tr("action_add_custom") == "Eigenen Punkt hinzufügen"
    assert tr("canvas_x_axis") == "X (Meter)"

    # Reset back to English default
    tm.set_language("en")
    assert tr("menu_file") == "File"


def test_undo_redo_lux_measurement_command():
    """Verify SetMeasurementLuxCommand undoes and redoes physical readings."""
    room = Room(length=6.0, width=4.0)
    proj = LuminationProject(name="Undo Test", room=room)
    p1 = MeasurementPoint(id="P1", x=1.0, y=1.0, lux=300.0)
    proj.points = [p1]

    cmd = SetMeasurementLuxCommand(proj, point_id="P1", new_lux=550.0, new_device="Lux Meter A")
    cmd.redo()
    assert p1.lux == 550.0
    assert p1.device_name == "Lux Meter A"

    cmd.undo()
    assert p1.lux == 300.0

    cmd.redo()
    assert p1.lux == 550.0


def test_undo_redo_add_and_delete_point_commands():
    """Verify AddPointCommand and DeletePointCommand correctly modify points collection."""
    room = Room(length=6.0, width=4.0)
    proj = LuminationProject(name="Add/Delete Test", room=room)
    p1 = MeasurementPoint(id="P1", x=1.0, y=1.0, lux=300.0)
    proj.points = [p1]

    # Add Point Command
    p2 = MeasurementPoint(id="C1", x=3.0, y=2.0, lux=450.0)
    add_cmd = AddPointCommand(proj, p2)
    add_cmd.redo()
    assert len(proj.points) == 2
    assert proj.find_point_by_id("C1") is not None

    add_cmd.undo()
    assert len(proj.points) == 1
    assert proj.find_point_by_id("C1") is None

    add_cmd.redo()
    assert len(proj.points) == 2

    # Delete Point Command
    del_cmd = DeletePointCommand(proj, "C1")
    del_cmd.redo()
    assert len(proj.points) == 1
    assert proj.find_point_by_id("C1") is None

    del_cmd.undo()
    assert len(proj.points) == 2
    assert proj.find_point_by_id("C1") is not None


def test_grid_generation_by_spacing_in_meters():
    """Verify grid generation using distance in meters."""
    room = Room(length=6.0, width=4.0, wall_margin=0.5)
    proj = LuminationProject(name="Spacing Grid", room=room)

    # Room effective length = 5.0m, effective width = 3.0m
    # Desired spacing = 1.0m -> 5 cols, 3 rows = 15 points
    proj.regenerate_grid(mode="spacing", spacing_x=1.0, spacing_y=1.0, wall_margin=0.5, centered_in_cells=True)
    assert len(proj.points) == 15
    assert proj.room.grid_cols == 5
    assert proj.room.grid_rows == 3

    # Check spacing along X is 1.0m
    xs = sorted(list({round(p.x, 3) for p in proj.points}))
    assert len(xs) == 5
    dx = xs[1] - xs[0]
    assert pytest.approx(dx, 0.01) == 1.0
