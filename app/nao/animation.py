import time
import tkinter as tk

from .config import ANIMATION_ROWS, ASSET_DIR, CELL_H, CELL_W


class SpriteAnimator:
    """Load an atlas once and drive sprite state independently of the UI."""

    def __init__(self, root, label, theme="uniform"):
        self.root, self.label = root, label
        self.state, self.frame_index, self.state_until = "idle", 0, 0.0
        self.sheet = None
        self.frames = {}
        self.load_theme(theme)

    def load_theme(self, theme):
        asset = ASSET_DIR / f"{theme}.png"
        if not asset.exists():
            raise FileNotFoundError(f"Missing theme atlas: {asset}")
        self.sheet = tk.PhotoImage(file=str(asset))
        self.frames = {}
        for state, row in ANIMATION_ROWS.items():
            row_frames = []
            for col in range(8):
                image = tk.PhotoImage(width=CELL_W, height=CELL_H)
                x, y = col * CELL_W, row * CELL_H
                image.tk.call(str(image), "copy", str(self.sheet), "-from", x, y, x + CELL_W, y + CELL_H)
                row_frames.append(image)
            self.frames[state] = row_frames

    def set_state(self, state, seconds=3):
        self.state = state if state in self.frames else "idle"
        self.frame_index = 0
        self.state_until = time.time() + seconds if seconds else 0

    def start(self):
        self._advance()

    def _advance(self):
        if self.state_until and time.time() > self.state_until:
            self.state, self.state_until = "idle", 0
        frames = self.frames[self.state]
        self.label.configure(image=frames[self.frame_index % len(frames)])
        self.frame_index += 1
        self.root.after(125, self._advance)
