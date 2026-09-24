import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from nao.storage import Store
from nao.timers import TimerService, WaterReminderService


class StorageTests(unittest.TestCase):
    def test_existing_data_is_preserved_and_defaults_are_added(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            path.write_text(json.dumps({"profile": {"nickname": "测试主人"}}), encoding="utf-8")
            store = Store(path)
            self.assertEqual(store.data["profile"]["nickname"], "测试主人")
            self.assertIn("settings", store.data)
            self.assertEqual(store.data["schema_version"], 1)

    def test_timer_expiry_clears_persisted_timer(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory) / "data.json")
            store.data["timer"] = {"kind": "focus", "ends_at": time.time() - 1}
            store.save()
            status = TimerService(store).status()
            self.assertTrue(status["finished"])
            self.assertIsNone(store.data["timer"])

    def test_paused_timer_survives_store_reload_and_resumes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            store = Store(path)
            timer = TimerService(store)
            timer.start("focus", 10)
            self.assertTrue(timer.pause())
            reloaded = Store(path)
            paused = TimerService(reloaded).status()
            self.assertTrue(paused["paused"])
            self.assertGreater(paused["remaining"], 0)
            self.assertTrue(TimerService(reloaded).resume())
            self.assertFalse(TimerService(reloaded).status()["paused"])

    def test_water_reminder_catches_up_once_and_schedules_future(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory) / "data.json")
            water = WaterReminderService(store)
            water.enable(30)
            water.config["next_at"] = time.time() - 95 * 60
            store.save()
            first = water.status()
            second = water.status()
            self.assertTrue(first["due"])
            self.assertGreaterEqual(first["missed"], 4)
            self.assertFalse(second["due"])
            self.assertGreater(second["remaining"], 0)


if __name__ == "__main__":
    unittest.main()
