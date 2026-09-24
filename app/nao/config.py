import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("LOCALAPPDATA", Path.home())) / "NaoCompanion"
DATA_FILE = DATA_DIR / "data.json"
COMMAND_DIR = DATA_DIR / "commands"
ASSET_DIR = APP_DIR / "assets"

CELL_W, CELL_H = 192, 208
ANIMATION_ROWS = {
    "idle": 0, "right": 1, "left": 2, "wave": 3, "jump": 4,
    "sad": 5, "waiting": 6, "working": 7, "done": 8,
}

DEFAULT_DATA = {
    "schema_version": 1,
    "profile": {
        "nickname": "主人", "city": "上海", "preferences": {},
        "projects": [], "habits": [],
    },
    "settings": {
        "focus_minutes": 25, "rest_minutes": 5, "water_minutes": 45,
        "clipboard_history": False, "voice": True, "theme": "uniform",
    },
    "todos": [], "calendar": [], "clipboard": [],
    "affection": {"points": 0, "interactions": 0, "last_day": ""},
    "timer": None,
}
