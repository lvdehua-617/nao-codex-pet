import ctypes
import json
import threading
import urllib.parse
import urllib.request


def media_key(vk):
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)


def fetch_weather_async(city, callback):
    def work():
        try:
            query = urllib.parse.urlencode({"name": city, "count": 1, "language": "zh", "format": "json"})
            geo = json.load(urllib.request.urlopen("https://geocoding-api.open-meteo.com/v1/search?" + query, timeout=8))
            location = geo["results"][0]
            forecast_query = urllib.parse.urlencode({
                "latitude": location["latitude"], "longitude": location["longitude"],
                "current": "temperature_2m,apparent_temperature,weather_code",
            })
            current = json.load(urllib.request.urlopen(
                "https://api.open-meteo.com/v1/forecast?" + forecast_query, timeout=8))["current"]
            message = f"{city}现在 {current['temperature_2m']}°C，体感 {current['apparent_temperature']}°C。"
        except (OSError, KeyError, IndexError, ValueError, json.JSONDecodeError):
            message = "天气没查到……网络好像在闹别扭。"
        callback(message)
    threading.Thread(target=work, daemon=True).start()
