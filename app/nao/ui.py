import datetime as dt
import json
import random
import threading
import tkinter as tk
from tkinter import simpledialog, ttk

from .ai import AIClient
from .animation import SpriteAnimator
from .config import COMMAND_DIR, DATA_FILE
from .speech import SpeechService
from .storage import Store
from .system_tools import fetch_weather_async, media_key
from .timers import TIMER_LABELS, TimerService

class NaoApp:
    def __init__(self):
        self.store = Store()
        self.timer_service = TimerService(self.store)
        self.speech_service = SpeechService()
        self.ai_client = AIClient()
        self.root = tk.Tk()
        self.root.title("奈绪助手")
        self.root.geometry("310x350+{}+{}".format(
            self.root.winfo_screenwidth() - 350, self.root.winfo_screenheight() - 450))
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.transparent = "#ff00ff"
        self.root.configure(bg=self.transparent)
        try:
            self.root.wm_attributes("-transparentcolor", self.transparent)
        except tk.TclError:
            pass

        self.bubble = tk.Label(self.root, text="主人，奈绪来陪你啦。", bg="#fffafc", fg="#493d55",
                               font=("Microsoft YaHei UI", 10), wraplength=260, justify="left",
                               padx=12, pady=8, relief="solid", borderwidth=1)
        self.bubble.pack(pady=(4, 0))
        self.sprite = tk.Label(self.root, bg=self.transparent, borderwidth=0)
        self.sprite.pack()
        self.animator = SpriteAnimator(self.root, self.sprite, self.store.data["settings"]["theme"])
        self.drag_xy = None
        self.last_clipboard = ""
        self.build_menu()
        self.sprite.bind("<Button-1>", self.click)
        self.sprite.bind("<Double-Button-1>", lambda _e: self.open_panel())
        self.sprite.bind("<Button-3>", lambda e: self.menu.tk_popup(e.x_root, e.y_root))
        self.sprite.bind("<B1-Motion>", self.drag)
        self.sprite.bind("<ButtonRelease-1>", lambda _e: setattr(self, "drag_xy", None))
        self.animator.start()
        self.root.after(500, self.poll)
        self.root.after(1000, self.tick)
        self.say("主人，奈绪已经准备好了。双击我可以打开控制面板。", speak=False)

    def build_menu(self):
        self.menu = tk.Menu(self.root, tearoff=False)
        self.menu.add_command(label="控制面板", command=self.open_panel)
        self.menu.add_command(label="开始 25 分钟专注", command=lambda: self.start_timer("focus", 25))
        self.menu.add_command(label="喝水提醒", command=lambda: self.start_timer("water", self.store.data["settings"]["water_minutes"]))
        self.menu.add_separator()
        self.menu.add_command(label="播放 / 暂停音乐", command=lambda: self.media_key(0xB3))
        self.menu.add_command(label="下一首", command=lambda: self.media_key(0xB0))
        self.menu.add_separator()
        self.menu.add_command(label="退出奈绪", command=self.root.destroy)

    def set_state(self, state, seconds=3):
        self.animator.set_state(state, seconds)

    def say(self, text, state="wave", speak=None):
        self.bubble.config(text=text)
        self.set_state(state, 4)
        if speak is None:
            speak = self.store.data["settings"]["voice"]
        if speak:
            self.speech_service.speak(text)

    def click(self, event):
        self.drag_xy = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())
        points = self.store.add_affection(1)
        level = self.level(points)[0]
        lines = [f"{self.nickname()}，才、才不是特意等你呢。",
                 f"唔……再陪奈绪一会儿嘛，{self.nickname()}。",
                 "摸头的话，好感度可是会偷偷增加的哦。"]
        self.say(random.choice(lines) + f"（{level}）", "jump", speak=False)

    def drag(self, event):
        if self.drag_xy:
            self.root.geometry(f"+{event.x_root-self.drag_xy[0]}+{event.y_root-self.drag_xy[1]}")

    def poll(self):
        for file in sorted(COMMAND_DIR.glob("*.json")):
            try:
                command = json.loads(file.read_text(encoding="utf-8"))
                self.handle_command(command)
            except Exception as exc:
                self.bubble.config(text=f"指令读取失败：{exc}")
            finally:
                try: file.unlink()
                except OSError: pass
        self.poll_clipboard()
        self.root.after(500, self.poll)

    def handle_command(self, c):
        action = c.get("action")
        if action == "status":
            kind = c.get("status", "working")
            state = {"working": "working", "waiting": "waiting", "complete": "done", "failed": "sad"}.get(kind, "idle")
            self.say(c.get("message", "奈绪收到啦。"), state, speak=kind in ("complete", "failed"))
        elif action == "say":
            self.say(c.get("message", "主人？"), c.get("animation", "wave"))
        elif action == "timer":
            self.start_timer(c.get("kind", "focus"), int(c.get("minutes", 25)))
        elif action == "remember":
            self.remember(c.get("key", "note"), c.get("value", ""))

    def tick(self):
        status = self.timer_service.status()
        if status and status["finished"]:
            self.say(status["message"], "wave", True)
        elif status:
            minutes, seconds = divmod(status["remaining"], 60)
            self.bubble.config(text=f"{TIMER_LABELS[status['kind']]}中 · {minutes:02d}:{seconds:02d}\n奈绪会安静陪着你。")
            self.animator.set_state("working", 0)
        self.root.after(1000, self.tick)

    def start_timer(self, kind, minutes):
        self.timer_service.start(kind, minutes)
        self.say(f"{TIMER_LABELS.get(kind, '计时')}开始，{minutes} 分钟后奈绪叫你。", "wave", False)

    def nickname(self):
        return self.store.data["profile"].get("nickname") or "主人"

    def remember(self, key, value):
        self.store.remember(key, value)

    def level(self, points=None):
        p = self.store.data["affection"]["points"] if points is None else points
        if p >= 200: return "心意相通", 4
        if p >= 80: return "十分依赖", 3
        if p >= 30: return "渐渐亲近", 2
        return "初次相伴", 1

    def poll_clipboard(self):
        if not self.store.data["settings"]["clipboard_history"]:
            return
        try:
            value = self.root.clipboard_get().strip()
            if value and value != self.last_clipboard and len(value) < 5000:
                self.last_clipboard = value
                history = self.store.data["clipboard"]
                history.insert(0, {"text": value, "at": dt.datetime.now().isoformat(timespec="seconds")})
                del history[30:]
                self.store.save()
        except tk.TclError:
            pass

    def media_key(self, vk):
        media_key(vk)
        self.say("好啦，音乐交给奈绪。", "wave", False)

    def weather(self):
        city = self.store.data["profile"].get("city", "上海")
        fetch_weather_async(city, lambda text: self.root.after(0, lambda: self.say(text, "wave", False)))

    def listen(self):
        self.say("奈绪在听，请说话……", "waiting", False)
        self.speech_service.listen_async(lambda heard: self.root.after(0, lambda: self.voice_reply(heard)))

    def voice_reply(self, heard):
        if not heard:
            self.say("没听清……可以靠近一点再说一次吗？", "sad", False); return
        text = heard.lower()
        if "天气" in text: self.weather(); return
        if "专注" in text or "番茄" in text: self.start_timer("focus", self.store.data["settings"]["focus_minutes"]); return
        if "播放" in text or "暂停" in text: self.media_key(0xB3); return
        if "好感" in text:
            self.say(f"现在是「{self.level()[0]}」，才没有每天都在数呢。", "waiting"); return
        if self.ai_client.configured:
            self.say("稍等一下，奈绪正在想……", "working", False)
            threading.Thread(target=self.ask_model, args=(heard,), daemon=True).start(); return
        self.say(f"奈绪听见了：{heard}。嗯……我会记在心里的。", "wave")

    def ask_model(self, prompt):
        try:
            answer = self.ai_client.ask(prompt)
        except (OSError, KeyError, ValueError, json.JSONDecodeError):
            answer = "模型连接失败了……请检查 API 地址、模型名和密钥。"
        self.root.after(0, lambda: self.say(answer, "wave", True))

    def open_panel(self):
        win = tk.Toplevel(self.root)
        win.title("奈绪助手控制面板")
        win.geometry("620x520")
        tabs = ttk.Notebook(win); tabs.pack(fill="both", expand=True, padx=10, pady=10)
        home = ttk.Frame(tabs); tasks = ttk.Frame(tabs); memory = ttk.Frame(tabs); tools = ttk.Frame(tabs); wardrobe = ttk.Frame(tabs)
        tabs.add(home, text="陪伴"); tabs.add(tasks, text="待办与日程"); tabs.add(memory, text="本地记忆")
        tabs.add(tools, text="桌面工具"); tabs.add(wardrobe, text="换装")

        ttk.Label(home, text=f"好感度：{self.store.data['affection']['points']} · {self.level()[0]}", font=("Microsoft YaHei UI", 14)).pack(pady=18)
        ttk.Button(home, text="🎙 点击说话", command=self.listen).pack(pady=6)
        ttk.Button(home, text="开始专注", command=lambda: self.start_timer("focus", self.store.data["settings"]["focus_minutes"])).pack(pady=6)
        ttk.Button(home, text="开始休息", command=lambda: self.start_timer("rest", self.store.data["settings"]["rest_minutes"])).pack(pady=6)

        todo_list = tk.Listbox(tasks, height=8); todo_list.pack(fill="x", padx=12, pady=10)
        def refresh_todos():
            todo_list.delete(0, "end")
            for item in self.store.data["todos"]: todo_list.insert("end", ("✓ " if item.get("done") else "○ ") + item["title"])
        def add_todo():
            value = simpledialog.askstring("新增待办", "要做什么？", parent=win)
            if value: self.store.data["todos"].append({"title": value, "done": False}); self.store.save(); refresh_todos()
        def toggle_todo():
            if todo_list.curselection():
                i = todo_list.curselection()[0]; self.store.data["todos"][i]["done"] = not self.store.data["todos"][i].get("done"); self.store.save(); refresh_todos()
        ttk.Button(tasks, text="新增待办", command=add_todo).pack(side="left", padx=12)
        ttk.Button(tasks, text="完成 / 恢复", command=toggle_todo).pack(side="left"); refresh_todos()
        calendar_list = tk.Listbox(tasks, height=6); calendar_list.pack(fill="x", padx=12, pady=(45, 8))
        def refresh_calendar():
            calendar_list.delete(0, "end")
            for item in self.store.data["calendar"]: calendar_list.insert("end", f"{item['at']}  {item['title']}")
        def add_event():
            title = simpledialog.askstring("新增日程", "日程名称：", parent=win)
            if not title: return
            at = simpledialog.askstring("新增日程", "时间（例如 2026-09-18 14:00）：", parent=win)
            if at: self.store.data["calendar"].append({"title": title, "at": at}); self.store.save(); refresh_calendar()
        ttk.Button(tasks, text="新增日程", command=add_event).pack(padx=12, anchor="w"); refresh_calendar()

        for label, key in (("主人称呼", "nickname"), ("天气城市", "city")):
            row = ttk.Frame(memory); row.pack(fill="x", padx=16, pady=8)
            ttk.Label(row, text=label, width=12).pack(side="left")
            var = tk.StringVar(value=self.store.data["profile"].get(key, "")); ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
            ttk.Button(row, text="保存", command=lambda k=key, v=var: self.remember(k, v.get())).pack(side="left", padx=6)
        ttk.Label(memory, text=f"数据仅保存在：\n{DATA_FILE}", foreground="#666").pack(pady=20)
        ttk.Label(memory, text="AI 对话（可选）：设置 NAO_AI_API_KEY、NAO_AI_MODEL 和\nNAO_AI_BASE_URL，即可连接 OpenAI 兼容接口。", foreground="#666").pack(pady=4)

        ttk.Button(tools, text="查看天气", command=self.weather).pack(pady=10)
        ttk.Button(tools, text="播放 / 暂停", command=lambda: self.media_key(0xB3)).pack(pady=5)
        ttk.Button(tools, text="上一首", command=lambda: self.media_key(0xB1)).pack(pady=5)
        ttk.Button(tools, text="下一首", command=lambda: self.media_key(0xB0)).pack(pady=5)
        clip = tk.BooleanVar(value=self.store.data["settings"]["clipboard_history"])
        def set_clip(): self.store.data["settings"]["clipboard_history"] = clip.get(); self.store.save()
        ttk.Checkbutton(tools, text="记录剪贴板历史（最多 30 条，仅本机）", variable=clip, command=set_clip).pack(pady=14)

        ttk.Label(wardrobe, text="制服", font=("Microsoft YaHei UI", 13)).pack(pady=(25, 5))
        ttk.Label(wardrobe, text="当前已安装 · 完整动画资源").pack()
        ttk.Separator(wardrobe).pack(fill="x", padx=40, pady=20)
        ttk.Label(wardrobe, text="睡衣、节日服装", font=("Microsoft YaHei UI", 13)).pack(pady=5)
        ttk.Label(wardrobe, text="换装引擎已就绪；需要为每套服装安装对应的 8×11 动画图集。", wraplength=480).pack()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    if not ASSET.exists():
        raise SystemExit(f"Missing sprite asset: {ASSET}")
    NaoApp().run()
