"""Demonstration generator script.

Generates sample project data, exports CSV, and creates a sample PDF report
in the project directory for instant user inspection.
"""

import os
from models.room import Room
from models.project import LuminationProject
from persistence.project_io import save_project
from persistence.csv_io import export_measurements_to_csv
from reporting.pdf_report import generate_pdf_report
from reporting.chart_exporter import export_room_map_image

def generate_samples():
    sample_dir = os.path.join(os.path.dirname(__file__), "samples")
    os.makedirs(sample_dir, exist_ok=True)

    # 1. Create realistic 7.0m x 5.0m Office Room Survey
    room = Room(
        name="Main Design Studio",
        length=7.0,
        width=5.0,
        height=3.0,
        measurement_plane_height=0.75,
        wall_margin=0.5,
        grid_rows=4,
        grid_cols=5,
    )
    project = LuminationProject(
        name="Design Studio Lighting Audit",
        author="Lighting Engineer",
        room=room,
        target_lux=500.0,
    )
    project.regenerate_grid(mode="count", rows=4, cols=5, wall_margin=0.5, centered_in_cells=True)

    # Realistic physical lux values with natural falloff from windows and light fixtures
    # Center rows have high illuminance (near 500-600 lx), edges near 320-400 lx
    lux_readings = [
        340, 390, 430, 410, 360,
        380, 480, 540, 520, 420,
        410, 520, 590, 560, 440,
        350, 430, 490, 460, 380,
    ]
    exp_readings = [
        360, 400, 450, 430, 380,
        400, 500, 550, 530, 440,
        430, 530, 600, 570, 450,
        370, 440, 500, 470, 390,
    ]

    for i, pt in enumerate(project.points):
        if i < len(lux_readings):
            pt.record_reading(float(lux_readings[i]))
            pt.expected_lux = float(exp_readings[i])

    # 2. Save .luxproj
    proj_file = os.path.join(sample_dir, "design_studio_survey.luxproj")
    save_project(project, proj_file)
    print(f"Sample project saved to: {proj_file}")

    # 3. Export CSV
    csv_file = os.path.join(sample_dir, "design_studio_measurements.csv")
    export_measurements_to_csv(project, csv_file)
    print(f"Sample CSV exported to: {csv_file}")

    # 4. Generate PDF Report
    pdf_file = os.path.join(sample_dir, "design_studio_report.pdf")
    generate_pdf_report(project, pdf_file)
    print(f"Sample PDF Report generated at: {pdf_file}")

    # 5. Export high-res map image
    img_file = os.path.join(sample_dir, "design_studio_map.png")
    export_room_map_image(project, output_path=img_file, dpi=300)
    print(f"Sample High-Res Map image saved to: {img_file}")

if __name__ == "__main__":
    generate_samples()
