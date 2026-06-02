"""ตั้งค่าครั้งแรก — รัน: python setup.py"""

import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR / ".env"
REQ_FILE = BASE_DIR / "requirements.txt"
ENV_EXAMPLE = BASE_DIR / ".env.example"


def _prompt(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    value = input(f"{label}{hint}: ").strip()
    return value or default


def main() -> int:
    print("=" * 50)
    print("  CBS Bot — ตั้งค่าครั้งแรก (โหมดส่วนตัว)")
    print("=" * 50)
    print()

    # 1. สร้าง .env
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            print(f"[OK] สร้าง {ENV_FILE.name} จาก .env.example")
        else:
            ENV_FILE.write_text(
                "CHANNEL_ACCESS_TOKEN=\nCHANNEL_SECRET=\nMY_LINE_USER_ID=\n"
                "DEFAULT_CITY=กรุงเทพ\nENABLE_MONITOR=true\nPORT=5000\n",
                encoding="utf-8",
            )
            print(f"[OK] สร้าง {ENV_FILE.name}")

    # 2. อ่านค่าปัจจุบัน
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    current = {}
    for line in lines:
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            current[k.strip()] = v.strip()

    print()
    print("กรอกข้อมูลจาก LINE Developers Console")
    print("(https://developers.line.biz/console/)")
    print("กด Enter เพื่อข้ามถ้ายังไม่มี\n")

    token = _prompt("CHANNEL_ACCESS_TOKEN", current.get("CHANNEL_ACCESS_TOKEN", ""))
    secret = _prompt("CHANNEL_SECRET", current.get("CHANNEL_SECRET", ""))
    city = _prompt("จังหวัดเริ่มต้น", current.get("DEFAULT_CITY", "กรุงเทพ"))
    port = _prompt("PORT (พอร์ตรัน bot)", current.get("PORT", "5000"))

    # 3. เขียน .env ใหม่
    new_env = f"""# CBS Bot — โหมดส่วนตัว (สร้างโดย setup.py)
CHANNEL_ACCESS_TOKEN={token}
CHANNEL_SECRET={secret}

# ใส่หลังรัน bot แล้วพิมพ์ "id" ใน LINE
MY_LINE_USER_ID={current.get("MY_LINE_USER_ID", "")}

DEFAULT_CITY={city}
ENABLE_MONITOR=true
PORT={port}

# ไม่บังคับ — แจ้งเตือนฝน
OPENWEATHER_API_KEY={current.get("OPENWEATHER_API_KEY", "")}

# ENCRYPTION_KEY สร้างอัตโนมัติใน data/.local_key
"""
    ENV_FILE.write_text(new_env, encoding="utf-8")
    print(f"\n[OK] บันทึก {ENV_FILE.name}")

    # 4. ติดตั้ง dependencies
    print("\nกำลังติดตั้ง packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE), "-q"])
    print("[OK] ติดตั้ง packages เรียบร้อย")

    print()
    print("-" * 50)
    print("ขั้นตอนถัดไป:")
    print("  1. รัน bot:   .\\run.ps1   หรือ   python main.py")
    print("  2. เปิด tunnel (เลือกอย่างใดอย่างหนึ่ง):")
    print("       ngrok http 5000")
    print("       cloudflared tunnel --url http://127.0.0.1:5000")
    print("  3. ตั้ง Webhook URL ใน LINE Console:")
    print("       https://xxxx.ngrok.io/webhook")
    print("  4. เปิด LINE แล้วพิมพ์  id  →  copy User ID")
    print("  5. ใส่ MY_LINE_USER_ID ใน .env แล้วรัน bot ใหม่")
    print("-" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
