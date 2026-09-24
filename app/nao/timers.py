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
        self.store.data["timer"] = {"kind": kind, "ends_at": time.time() + int(minutes) * 60}
        self.store.save()

    def cancel(self):
        self.store.data["timer"] = None
        self.store.save()

    def status(self):
        timer = self.store.data.get("timer")
        if not timer:
            return None
        remaining = int(timer["ends_at"] - time.time())
        if remaining <= 0:
            kind = timer["kind"]
            self.cancel()
            return {"finished": True, "kind": kind, "message": TIMER_MESSAGES.get(kind, "提醒时间到啦。")}
        return {"finished": False, "kind": timer["kind"], "remaining": remaining}
