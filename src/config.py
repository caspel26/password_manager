from pathlib import Path

VERSION = 'v1.0.0'

DEFAULT_GUI_SIZES = [("primary", "800x600"), ("secondary", "600x400")]
FILES_TYPE = [
    ("All Files", "*.*"),
    ("Private key", "*.key"),
    ("Text Document", "*.txt"),
    ("PEM", "*.pem, *.cer, *.crt"),
    ("DER", "*.der"),
]
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_DIR = BASE_DIR / 'images'
ICON = IMG_DIR / 'icon.ico'
