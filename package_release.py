"""Create clean Release folder structure for distribution."""

import os
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(ROOT_DIR, "dist", "Lumination")
RELEASE_DIR = os.path.join(ROOT_DIR, "release", "Lumination")

def main():
    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)

    os.makedirs(os.path.dirname(RELEASE_DIR), exist_ok=True)
    print(f"Copying from {DIST_DIR} to {RELEASE_DIR}...")
    shutil.copytree(DIST_DIR, RELEASE_DIR)

    # Add quickstart README in release folder
    readme_path = os.path.join(RELEASE_DIR, "README_QUICKSTART.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("=" * 65 + "\n")
        f.write("LUMINATION — REAL-ROOM ILLUMINANCE SURVEY & ANALYSIS\n")
        f.write("=" * 65 + "\n\n")
        f.write("HOW TO LAUNCH:\n")
        f.write("Double-click 'Lumination.exe' to start the application.\n\n")
        f.write("KEY FEATURES:\n")
        f.write("1. Create room and define survey grid (by count or target spacing).\n")
        f.write("2. Serpentine walking traversal order for physical walkthroughs.\n")
        f.write("3. Dedicated Survey Mode bar: type lux reading, press Enter to advance.\n")
        f.write("4. Live Photometric KPIs: E_avg, E_min, E_max, Uniformity U_0, Std Dev.\n")
        f.write("5. Scientific 2D False-Colour Heatmaps & Isolux Contours.\n")
        f.write("6. Comparison with Target Illuminance.\n")
        f.write("7. Non-destructive spatial outlier awareness.\n")
        f.write("8. Full CSV import/export and professional multi-page PDF reporting.\n\n")
        f.write("Enjoy using Lumination!\n")

    print("Release folder successfully prepared at:", RELEASE_DIR)
    exe_path = os.path.join(RELEASE_DIR, "Lumination.exe")
    print("Executable location:", exe_path)

if __name__ == "__main__":
    main()
