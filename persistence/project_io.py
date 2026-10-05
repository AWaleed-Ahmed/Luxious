"""Project File I/O Persistence.

Saves and loads Lumination project files (.luxproj or .json) in a clean,
documented JSON format.
"""

from __future__ import annotations
import json
import os
from typing import Dict, Any

from models.project import LuminationProject


def save_project(project: LuminationProject, file_path: str) -> None:
    """Save Lumination project to a JSON file (.luxproj)."""
    data = project.to_dict()
    # Ensure directory exists
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    project.file_path = file_path
    project.is_dirty = False


def load_project(file_path: str) -> LuminationProject:
    """Load Lumination project from a JSON file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Project file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    project = LuminationProject.from_dict(data)
    project.file_path = file_path
    project.is_dirty = False
    return project
