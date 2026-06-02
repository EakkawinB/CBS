"""Background monitor — แผ่นดินไหว + อากาศแบบละเอียดอัตโนมัติ"""

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
    SEVERE_WEATHER_COOLDOWN_SEC,
    WEATHER_REPORT_COOLDOWN_SEC,
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
        self._last_weather_report: dict[str, float] = {}

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
            event_ms = props.get("time")
            tsunami = props.get("tsunami", 0)
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
                    event_time = "-"
                    if event_ms:
                        event_time = time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(event_ms / 1000),
                        )
                    risk_tag = "สูง" if mag >= 6.0 else "ปานกลาง" if mag >= 5.0 else "เฝ้าระวัง"
                    tsunami_tag = "มีความเสี่ยง" if tsunami else "ไม่พบสัญญาณ"
                    self._push(
                        user["user_id"],
                        f"🚨 รายงานแผ่นดินไหวอัตโนมัติ\n"
                        f"📍 จุดศูนย์กลาง: {place}\n"
                        f"📊 ขนาด (Magnitude): {mag:.1f}\n"
                        f"⏰ เวลาเกิดเหตุ: {event_time}\n"
                        f"📏 ระยะจาก {city}: ~{int(dist)} กม.\n"
                        f"🌊 สถานะสึนามิ: {tsunami_tag}\n"
                        f"⚠️ ระดับเฝ้าระวัง: {risk_tag}\n"
                        f"💡 คำแนะนำ: อยู่ในจุดปลอดภัย ติดตามข่าวจากหน่วยงานทางการ",
                    )
            self._sent_eq_ids.add(eq_id)

    def check_weather(self, users: list[dict]) -> None:
        if not OPENWEATHER_API_KEY:
            return

        city_cache: dict[str, dict | None] = {}
        for user in users:
            if not user.get("alerts_enabled", True):
                continue
            city = user["city"]
            if city not in city_cache:
                query = get_weather_query(city)
                url = (
                    "https://api.openweathermap.org/data/2.5/weather"
                    f"?q={query},TH&appid={OPENWEATHER_API_KEY}&units=metric&lang=th"
                )
                try:
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    city_cache[city] = resp.json()
                except requests.RequestException as exc:
                    logger.warning("Weather API error (%s): %s", city, exc)
                    city_cache[city] = None

            w_data = city_cache[city]
            if not w_data or not w_data.get("weather"):
                continue

            uid = user["user_id"]
            now = time.time()
            weather_main = w_data["weather"][0].get("main", "")
            desc = w_data["weather"][0].get("description", "ไม่ทราบสภาพอากาศ")
            severe_types = {"Rain", "Drizzle", "Thunderstorm", "Squall", "Tornado"}
            is_severe = weather_main in severe_types

            last_weather = self._last_weather_report.get(uid, 0)
            last_severe = self._last_rain_alert.get(uid, 0)
            if is_severe:
                if now - last_severe < SEVERE_WEATHER_COOLDOWN_SEC:
                    continue
            elif now - last_weather < WEATHER_REPORT_COOLDOWN_SEC:
                continue

            temp = w_data.get("main", {}).get("temp")
            feels_like = w_data.get("main", {}).get("feels_like")
            humidity = w_data.get("main", {}).get("humidity")
            pressure = w_data.get("main", {}).get("pressure")
            wind_speed = w_data.get("wind", {}).get("speed")
            clouds = w_data.get("clouds", {}).get("all")
            rain_1h = w_data.get("rain", {}).get("1h")

            temp_str = f"{temp:.1f}°C" if temp is not None else "-"
            feels_str = f"{feels_like:.1f}°C" if feels_like is not None else "-"
            hum_str = f"{humidity}%" if humidity is not None else "-"
            pressure_str = f"{pressure} hPa" if pressure is not None else "-"
            wind_str = f"{wind_speed:.1f} m/s" if wind_speed is not None else "-"
            cloud_str = f"{clouds}%" if clouds is not None else "-"
            rain_str = f"{rain_1h:.1f} mm/1h" if rain_1h is not None else "0 mm/1h"

            icon = "🌩️" if weather_main == "Thunderstorm" else "🌧️" if weather_main in {"Rain", "Drizzle"} else "⛅"
            level = "เร่งด่วน" if is_severe else "รายงานทั่วไป"
            suggestion = (
                "พกร่ม/หลีกเลี่ยงพื้นที่น้ำท่วมขัง และเฝ้าระวังฟ้าผ่า"
                if is_severe
                else "วางแผนเดินทางได้ตามปกติ และติดตามการเปลี่ยนแปลงของอากาศ"
            )
            self._push(
                uid,
                f"{icon} รายงานสภาพอากาศอัตโนมัติ ({level})\n"
                f"📍 พื้นที่: {city}\n"
                f"🌤️ สภาพอากาศ: {desc}\n"
                f"🌡️ อุณหภูมิ: {temp_str}\n"
                f"🤒 รู้สึกเหมือน: {feels_str}\n"
                f"💧 ความชื้น: {hum_str}\n"
                f"🌬️ ลม: {wind_str}\n"
                f"☁️ เมฆปกคลุม: {cloud_str}\n"
                f"🌧️ ปริมาณฝน: {rain_str}\n"
                f"🧭 ความกดอากาศ: {pressure_str}\n"
                f"💡 คำแนะนำ: {suggestion}",
            )
            self._last_weather_report[uid] = now
            if is_severe:
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
                    self.check_weather(users)
            except Exception as exc:
                logger.exception("Monitor error: %s", exc)
            time.sleep(MONITOR_INTERVAL_SEC)
