# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification file for Lumination Desktop Application.

Packages all core and lazy-loaded modules (PySide6, NumPy, SciPy, Matplotlib, ReportLab)
into a standalone Windows desktop executable with zero console window.
"""

import sys
import os

block_cipher = None
project_dir = os.path.abspath(SPECPATH)

hidden_imports = [
    # Core PySide6
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    
    # NumPy & Scientific stack
    'numpy',
    'numpy.core._methods',
    'numpy.lib.format',
    
    # SciPy (lazy-loaded modules)
    'scipy',
    'scipy.interpolate',
    'scipy.interpolate.griddata',
    'scipy.interpolate.RBFInterpolator',
    'scipy.spatial',
    'scipy.spatial.qhull',
    'scipy.spatial.distance',
    'scipy.special',
    
    # Matplotlib
    'matplotlib',
    'matplotlib.backends.backend_qtagg',
    'matplotlib.backends.backend_agg',
    'matplotlib.figure',
    'matplotlib.ticker',
    'matplotlib.patches',
    'matplotlib.path',
    'matplotlib.colors',
    'matplotlib.cm',
    'matplotlib.colorbar',
    
    # ReportLab (lazy-loaded PDF engine)
    'reportlab',
    'reportlab.platypus',
    'reportlab.platypus.flowables',
    'reportlab.platypus.paragraph',
    'reportlab.platypus.tables',
    'reportlab.platypus.doctemplate',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.colors',
    'reportlab.lib.styles',
    'reportlab.lib.units',
    'reportlab.pdfgen.canvas',
    
    # Application packages
    'models.measurement',
    'models.room',
    'models.project',
    'analysis.statistics',
    'analysis.interpolation',
    'analysis.contours',
    'analysis.comparison',
    'analysis.outliers',
    'visualization.map_plotter',
    'visualization.chart_plotter',
    'visualization.color_maps',
    'measurement_sources.base',
    'measurement_sources.manual',
    'measurement_sources.mock',
    'measurement_sources.usb_serial',
    'measurement_sources.bluetooth_meter',
    'persistence.project_io',
    'persistence.csv_io',
    'reporting.pdf_report',
    'reporting.chart_exporter',
    'ui.styles',
    'ui.main_window',
    'ui.room_canvas',
    'ui.survey_mode_widget',
    'ui.measurement_table',
    'ui.results_panel',
    'ui.target_panel',
    'ui.comparison_panel',
    'ui.layer_control_widget',
    'ui.dialogs.new_project_dialog',
    'ui.dialogs.grid_generator_dialog',
    'ui.dialogs.point_edit_dialog',
    'ui.dialogs.export_dialog',
    'ui.dialogs.hardware_connection_dialog',
    'i18n.translations',
    'utils.undo_commands',
    'ui.icons',
]

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'pandas', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Lumination',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No command prompt window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Lumination',
)
