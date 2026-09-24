import time


TIMER_LABELS = {"focus": "专注", "rest": "休息", "water": "喝水提醒"}
TIMER_MESSAGES = {
    "focus": "专注完成啦！休息一下吧，主人。",
    "rest": "休息结束，该回来啦。奈绪会陪着你的。",
    "water": "到喝水时间啦！不许装作没听见哦。",
}


class TimerService:
    def __init__(self, store):
        self.store = store

    def start(self, kind, minutes):
        if kind not in TIMER_LABELS or not 1 <= int(minutes) <= 480:
            raise ValueError("Invalid timer")
        now = time.time()
        self.store.data["timer"] = {
            "kind": kind, "started_at": now, "duration_seconds": int(minutes) * 60,
            "ends_at": now + int(minutes) * 60, "paused": False,
        }
        self.store.save()

    def pause(self):
        timer = self.store.data.get("timer")
        if not timer or timer.get("paused"):
            return False
        timer["remaining_seconds"] = max(0, int(timer["ends_at"] - time.time()))
        timer["paused"] = True
        self.store.save()
        return True

    def resume(self):
        timer = self.store.data.get("timer")
        if not timer or not timer.get("paused"):
            return False
        timer["ends_at"] = time.time() + max(1, int(timer.pop("remaining_seconds", 1)))
        timer["paused"] = False
        self.store.save()
        return True

    def cancel(self):
        self.store.data["timer"] = None
        self.store.save()

    def status(self):
        timer = self.store.data.get("timer")
        if not timer:
            return None
        if timer.get("paused"):
            return {"finished": False, "paused": True, "kind": timer["kind"],
                    "remaining": max(0, int(timer.get("remaining_seconds", 0)))}
        remaining = int(timer["ends_at"] - time.time())
        if remaining <= 0:
            kind = timer["kind"]
            overdue = abs(remaining)
            self.cancel()
            return {"finished": True, "kind": kind, "overdue": overdue,
                    "message": TIMER_MESSAGES.get(kind, "提醒时间到啦。")}
        return {"finished": False, "paused": False, "kind": timer["kind"], "remaining": remaining}


class WaterReminderService:
    """Persistent repeating reminder that advances past missed intervals once."""

    def __init__(self, store):
        self.store = store

    @property
    def config(self):
        return self.store.data["reminders"]["water"]

    def enable(self, minutes=None):
        interval = int(minutes or self.store.data["settings"]["water_minutes"])
        if not 1 <= interval <= 1440:
            raise ValueError("Invalid water interval")
        self.config.update({"enabled": True, "interval_minutes": interval,
                            "next_at": time.time() + interval * 60})
        self.store.data["settings"]["water_minutes"] = interval
        self.store.save()

    def disable(self):
        self.config.update({"enabled": False, "next_at": None})
        self.store.save()

    def status(self):
        reminder = self.config
        if not reminder.get("enabled"):
            return None
        interval = max(60, int(reminder.get("interval_minutes", 45)) * 60)
        next_at = reminder.get("next_at")
        if not isinstance(next_at, (int, float)):
            reminder["next_at"] = time.time() + interval
            self.store.save()
            return {"due": False, "remaining": interval}
        remaining = int(next_at - time.time())
        if remaining > 0:
            return {"due": False, "remaining": remaining}
        missed = max(1, int((time.time() - next_at) // interval) + 1)
        reminder["next_at"] = next_at + missed * interval
        self.store.save()
        return {"due": True, "missed": missed, "remaining": int(reminder["next_at"] - time.time())}
