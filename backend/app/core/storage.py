from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
STORAGE_ROOT = BACKEND_DIR / "storage"
IMAGES_DIR = STORAGE_ROOT / "images"


def ensure_storage_dirs() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
