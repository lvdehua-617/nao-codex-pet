import subprocess
import threading

from .config import APP_DIR


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class SpeechService:
    def speak(self, text):
        threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    def _speak(self, text):
        safe = text.replace("'", "''")
        command = ("Add-Type -AssemblyName System.Speech; "
                   "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                   "$s.Rate=1; $s.Speak('{}')").format(safe)
        subprocess.run(["powershell", "-NoProfile", "-Command", command],
                       creationflags=CREATE_NO_WINDOW, check=False)

    def listen_async(self, callback):
        def work():
            try:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(APP_DIR / "speech-recognize.ps1")],
                    capture_output=True, text=True, timeout=18, creationflags=CREATE_NO_WINDOW,
                )
                heard = result.stdout.strip()
            except (OSError, subprocess.SubprocessError):
                heard = ""
            callback(heard)
        threading.Thread(target=work, daemon=True).start()
