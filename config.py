"""ตั้งค่า CBS Bot โหมดส่วนตัว — โหลด .env และสร้าง key อัตโนมัติ"""

import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
LOCAL_KEY_FILE = BASE_DIR / "data" / ".local_key"

load_dotenv(ENV_FILE)

# --- โหมดส่วนตัว (default) ---
PERSONAL_MODE = os.getenv("PERSONAL_MODE", "true").lower() in ("1", "true", "yes")

# LINE
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "").strip()
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "").strip()

# เจ้าของ bot คนเดียว — ใส่หลังพิมพ์คำสั่ง "id" ใน LINE
MY_LINE_USER_ID = os.getenv("MY_LINE_USER_ID", "").strip()

# External APIs (ไม่บังคับ)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()

# Security
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").strip()

# พื้นที่เริ่มต้น
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "กรุงเทพ").strip()

# Database
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "cbs.db"))

# Monitor — ปิดได้ถ้าไม่ต้องการแจ้งเตือนอัตโนมัติ
ENABLE_MONITOR = os.getenv("ENABLE_MONITOR", "true").lower() in ("1", "true", "yes")
EARTHQUAKE_RADIUS_KM = int(os.getenv("EARTHQUAKE_RADIUS_KM", "1500"))
EARTHQUAKE_MIN_MAG = float(os.getenv("EARTHQUAKE_MIN_MAG", "4.0"))
MONITOR_INTERVAL_SEC = int(os.getenv("MONITOR_INTERVAL_SEC", "600"))
RAIN_ALERT_COOLDOWN_SEC = int(os.getenv("RAIN_ALERT_COOLDOWN_SEC", "7200"))
WEATHER_REPORT_COOLDOWN_SEC = int(os.getenv("WEATHER_REPORT_COOLDOWN_SEC", "21600"))
SEVERE_WEATHER_COOLDOWN_SEC = int(os.getenv("SEVERE_WEATHER_COOLDOWN_SEC", "3600"))

# Server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Broadcast
BROADCAST_DELAY_SEC = float(os.getenv("BROADCAST_DELAY_SEC", "0.05"))
MAX_BROADCAST_LEN = int(os.getenv("MAX_BROADCAST_LEN", "2000"))


def _load_or_create_encryption_key() -> str:
    """ใช้ key จาก .env หรือสร้างเก็บใน data/.local_key (เครื่องส่วนตัว)"""
    global ENCRYPTION_KEY
    if ENCRYPTION_KEY:
        return ENCRYPTION_KEY

    if LOCAL_KEY_FILE.exists():
        ENCRYPTION_KEY = LOCAL_KEY_FILE.read_text(encoding="utf-8").strip()
        os.environ["ENCRYPTION_KEY"] = ENCRYPTION_KEY
        return ENCRYPTION_KEY

    LOCAL_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    LOCAL_KEY_FILE.write_text(ENCRYPTION_KEY, encoding="utf-8")
    os.environ["ENCRYPTION_KEY"] = ENCRYPTION_KEY
    return ENCRYPTION_KEY


def is_owner(user_id: str) -> bool:
    if MY_LINE_USER_ID:
        return user_id == MY_LINE_USER_ID
    return False


def missing_line_credentials() -> list[str]:
    missing = []
    if not CHANNEL_ACCESS_TOKEN:
        missing.append("CHANNEL_ACCESS_TOKEN")
    if not CHANNEL_SECRET:
        missing.append("CHANNEL_SECRET")
    return missing


def ensure_ready() -> list[str]:
    """เตรียม config ให้พร้อมรัน — คืนรายการที่ยังขาด"""
    _load_or_create_encryption_key()
    return missing_line_credentials()


# โหลด key ทันทีเมื่อ import (ไม่ต้องรัน setup แยก)
_load_or_create_encryption_key()
