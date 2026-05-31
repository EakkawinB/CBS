"""Background monitor — แผ่นดินไหว + ฝนตก"""

import logging
import math
import time

import requests
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

from cities import get_coords, get_weather_query
from config import (
    EARTHQUAKE_MIN_MAG,
    EARTHQUAKE_RADIUS_KM,
    MONITOR_INTERVAL_SEC,
    OPENWEATHER_API_KEY,
    RAIN_ALERT_COOLDOWN_SEC,
)
from database import Database

logger = logging.getLogger(__name__)


def calc_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class MonitorService:
    def __init__(self, line_api: LineBotApi, db: Database):
        self.line_api = line_api
        self.db = db
        self._sent_eq_ids: set[str] = set()
        self._last_rain_alert: dict[str, float] = {}

    def check_earthquakes(self, users: list[dict]) -> None:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for eq in data.get("features", []):
            eq_id = eq["id"]
            props = eq["properties"]
            mag = props.get("mag")
            place = props.get("place", "ไม่ทราบสถานที่")
            lon, lat = eq["geometry"]["coordinates"][:2]

            if not mag or mag < EARTHQUAKE_MIN_MAG or eq_id in self._sent_eq_ids:
                continue

            for user in users:
                if not user.get("alerts_enabled", True):
                    continue
                city = user["city"]
                coords = get_coords(city)
                if not coords:
                    continue
                lat_u, lon_u = coords
                dist = calc_distance_km(lat_u, lon_u, lat, lon)
                if dist <= EARTHQUAKE_RADIUS_KM:
                    self._push(
                        user["user_id"],
                        f"⚠️ แจ้งเตือนแผ่นดินไหว!\n"
                        f"📍 {place}\n"
                        f"ขนาด: {mag}\n"
                        f"📏 ห่างจาก {city} ~{int(dist)} กม.",
                    )
            self._sent_eq_ids.add(eq_id)

    def check_rain(self, users: list[dict]) -> None:
        if not OPENWEATHER_API_KEY:
            return

        for user in users:
            if not user.get("alerts_enabled", True):
                continue
            city = user["city"]
            query = get_weather_query(city)
            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?q={query},TH&appid={OPENWEATHER_API_KEY}&units=metric&lang=th"
            )
            try:
                resp = requests.get(url, timeout=10)
                resp.raise_for_status()
                w_data = resp.json()
            except requests.RequestException as exc:
                logger.warning("Weather API error (%s): %s", city, exc)
                continue

            weather_main = ""
            if w_data.get("weather"):
                weather_main = w_data["weather"][0].get("main", "")

            if weather_main not in ("Rain", "Drizzle", "Thunderstorm"):
                continue

            uid = user["user_id"]
            now = time.time()
            if now - self._last_rain_alert.get(uid, 0) < RAIN_ALERT_COOLDOWN_SEC:
                continue

            desc = w_data["weather"][0].get("description", "ฝนตก")
            temp = w_data.get("main", {}).get("temp")
            temp_str = f"\n🌡️ อุณหภูมิ: {temp:.0f}°C" if temp is not None else ""
            self._push(
                uid,
                f"🌧️ แจ้งเตือนฝนที่ {city}\n{desc}{temp_str}\nอย่าลืมดูแลสุขภาพนะครับ",
            )
            self._last_rain_alert[uid] = now

    def _push(self, user_id: str, text: str) -> None:
        try:
            self.line_api.push_message(user_id, TextSendMessage(text=text))
        except LineBotApiError as exc:
            logger.warning("Push failed %s: %s", user_id[:8], exc.message)

    def run_loop(self) -> None:
        logger.info("Monitor started (interval=%ss)", MONITOR_INTERVAL_SEC)
        while True:
            try:
                users = self.db.get_subscribers(alerts_only=True)
                if users:
                    self.check_earthquakes(users)
                    self.check_rain(users)
            except Exception as exc:
                logger.exception("Monitor error: %s", exc)
            time.sleep(MONITOR_INTERVAL_SEC)
