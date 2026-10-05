"""Color map definitions and palette configurations for scientific lighting visualization."""

from typing import List, Dict

AVAILABLE_COLORMAPS: Dict[str, str] = {
    "viridis": "Viridis (Perceptually Uniform)",
    "plasma": "Plasma (High Contrast)",
    "turbo": "Turbo (Enhanced Rainbow)",
    "inferno": "Inferno (Thermal Warm)",
    "coolwarm": "Cool-Warm (Diverging)",
    "cividis": "Cividis (Colorblind Safe)",
    "YlOrRd": "Yellow-Orange-Red (Illuminance Standard)",
}

DEFAULT_COLORMAP = "viridis"
