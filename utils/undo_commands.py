"""Undo / Redo Command Architecture for Lumination.

Uses PySide6.QtGui.QUndoCommand and QUndoStack to support full multi-level
undo/redo for measurement edits, point additions, point deletions, and grid modifications.
"""

from __future__ import annotations
from typing import Optional, List, Callable, Any
import copy
from PySide6.QtGui import QUndoCommand, QUndoStack

from models.project import LuminationProject
from models.measurement import MeasurementPoint


class SetMeasurementLuxCommand(QUndoCommand):
    """Command for recording/editing a lux reading on a point."""

    def __init__(
        self,
        project: LuminationProject,
        point_id: str,
        new_lux: Optional[float],
        new_device: Optional[str] = None,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(f"Edit Measurement {point_id}")
        self.project = project
        self.point_id = point_id
        self.new_lux = new_lux
        self.new_device = new_device
        self.callback = callback

        pt = project.find_point_by_id(point_id)
        if pt:
            self.old_lux = pt.lux
            self.old_timestamp = pt.timestamp
            self.old_device = pt.device_name
            self.old_outlier = pt.is_possible_outlier
            self.old_reason = pt.outlier_reason
        else:
            self.old_lux = None
            self.old_timestamp = None
            self.old_device = None
            self.old_outlier = False
            self.old_reason = ""

    def redo(self) -> None:
        pt = self.project.find_point_by_id(self.point_id)
        if pt:
            if self.new_lux is not None:
                pt.record_reading(self.new_lux, device_name=self.new_device)
            else:
                pt.clear_reading()
            self.project.mark_modified()
            if self.callback:
                self.callback()

    def undo(self) -> None:
        pt = self.project.find_point_by_id(self.point_id)
        if pt:
            pt.lux = self.old_lux
            pt.timestamp = self.old_timestamp
            pt.device_name = self.old_device
            pt.is_possible_outlier = self.old_outlier
            pt.outlier_reason = self.old_reason
            self.project.mark_modified()
            if self.callback:
                self.callback()


class AddPointCommand(QUndoCommand):
    """Command for adding a custom measurement point."""

    def __init__(
        self,
        project: LuminationProject,
        point: MeasurementPoint,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(f"Add Point {point.id}")
        self.project = project
        self.point = copy.deepcopy(point)
        self.callback = callback

    def redo(self) -> None:
        if not self.project.find_point_by_id(self.point.id):
            self.project.points.append(copy.deepcopy(self.point))
            self.project.mark_modified()
            if self.callback:
                self.callback()

    def undo(self) -> None:
        self.project.points = [p for p in self.project.points if p.id != self.point.id]
        self.project.mark_modified()
        if self.callback:
            self.callback()


class DeletePointCommand(QUndoCommand):
    """Command for deleting a measurement point."""

    def __init__(
        self,
        project: LuminationProject,
        point_id: str,
        callback: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(f"Delete Point {point_id}")
        self.project = project
        self.point_id = point_id
        self.callback = callback

        pt = project.find_point_by_id(point_id)
        self.deleted_point = copy.deepcopy(pt) if pt else None
        self.deleted_index = 0
        if pt:
            for idx, p in enumerate(project.points):
                if p.id == point_id:
                    self.deleted_index = idx
                    break

    def redo(self) -> None:
        if self.deleted_point:
            self.project.points = [p for p in self.project.points if p.id != self.point_id]
            self.project.mark_modified()
            if self.callback:
                self.callback()

    def undo(self) -> None:
        if self.deleted_point:
            # Reinsert at original index if possible
            insert_pos = min(self.deleted_index, len(self.project.points))
            self.project.points.insert(insert_pos, copy.deepcopy(self.deleted_point))
            self.project.mark_modified()
            if self.callback:
                self.callback()
