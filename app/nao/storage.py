import copy
import datetime as dt
import json
import threading

from .config import COMMAND_DIR, DATA_DIR, DATA_FILE, DEFAULT_DATA


def merge_defaults(value, defaults):
    result = value if isinstance(value, dict) else {}
    for key, item in defaults.items():
        if key not in result:
            result[key] = copy.deepcopy(item)
        elif isinstance(item, dict):
            result[key] = merge_defaults(result[key], item)
    return result


class Store:
    """Thread-safe JSON persistence with atomic writes and schema defaults."""

    def __init__(self, path=DATA_FILE):
        self.path = path
        self._lock = threading.RLock()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        COMMAND_DIR.mkdir(parents=True, exist_ok=True)
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = {}
        self.data = merge_defaults(loaded, DEFAULT_DATA)
        self.save()

    def save(self):
        with self._lock:
            temp = self.path.with_suffix(".tmp")
            temp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.replace(self.path)

    def add_affection(self, points=1):
        with self._lock:
            affection = self.data["affection"]
            affection["points"] += points
            affection["interactions"] += 1
            affection["last_day"] = dt.date.today().isoformat()
            self.save()
            return affection["points"]

    def remember(self, key, value):
        with self._lock:
            profile = self.data["profile"]
            if key in ("nickname", "city"):
                profile[key] = value
            else:
                profile["preferences"][key] = value
            self.save()

    @property
    def nickname(self):
        return self.data["profile"].get("nickname") or "主人"
