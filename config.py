"""
PulseShield Configuration and Constants
Defines facial landmark ROIs, perturbation parameters, UI theme colors, and paths.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "pulseshield.db"
TEMP_MEDIA_DIR = BASE_DIR / "temp_media"
TEMP_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Facial Landmark Region of Interest (ROI) Indices for MediaPipe Face Mesh
# Verified cheek indices from specification:
LEFT_CHEEK_LANDMARKS = [116, 123, 147, 213, 138, 135, 169, 170]
RIGHT_CHEEK_LANDMARKS = [345, 352, 376, 433, 367, 364, 394, 395]

# Anatomically reasonable forehead polygon (strictly skin, excluding eyebrows, eyes, and hairline)
# Landmark 10 (top midline), 109/67/103/54 (left forehead), 9/8 (above eyebrows), 284/332/297/338 (right forehead)
FOREHEAD_LANDMARKS = [10, 338, 297, 332, 284, 9, 54, 103, 67, 109]

# Face boundary contour (for static photo masking or boundary verification)
FACE_OVAL_LANDMARKS = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
]

# Perturbation Engine Defaults
DEFAULT_DELTA = 2.0
MIN_DELTA = 1.0
MAX_DELTA = 4.0
STEP_DELTA = 0.5

# Experimental Desynchronization Frequencies (Hz)
DEFAULT_EXPERIMENTAL_FREQ = 6.5  # Bounded high-frequency component
PHYSIOLOGICAL_BAND_LOW = 0.7    # ~42 bpm
PHYSIOLOGICAL_BAND_HIGH = 3.5   # ~210 bpm

# Missing Face Mask Re-use Cache Threshold (number of consecutive frames)
MAX_STALE_FRAMES = 5
MAX_FACE_DISPLACEMENT_PX = 45.0  # If face center moves more than this, invalidate stale mask

# UI Cyberpunk & Glassmorphism Theme Palette
THEME = {
    "bg_dark": "#0A0E17",
    "bg_card": "#111C35",
    "bg_surface": "#0E1726",
    "accent_cyan": "#00F0FF",
    "accent_blue": "#0066FF",
    "accent_purple": "#A855F7",
    "accent_green": "#10B981",
    "accent_red": "#EF4444",
    "accent_yellow": "#F59E0B",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "border_glow": "rgba(0, 240, 255, 0.25)",
}
