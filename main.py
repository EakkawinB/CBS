"""
CBS Bot — โหมดส่วนตัว
แจ้งเตือนแผ่นดินไหว/ฝน + ส่งข้อความ broadcast
"""

import logging
import os
import sys
import threading

from flask import Flask, jsonify, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from config import (
    CHANNEL_ACCESS_TOKEN,
    CHANNEL_SECRET,
    DEFAULT_CITY,
    ENABLE_MONITOR,
    HOST,
    MY_LINE_USER_ID,
    PORT,
    ensure_ready,
)
from database import get_db
from handlers import handle_message
from services.broadcast import BroadcastService
from services.monitor import MonitorService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cbs")


def print_banner(missing: list[str]):
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║       CBS Bot — โหมดส่วนตัว          ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    if missing:
        print("  ⚠  ยังตั้งค่าไม่ครบ:")
        for m in missing:
            print(f"     • {m}")
        print()
        print("  แก้ไข: python setup.py")
        print("  หรือเติมค่าใน .env")
        print()
        return
    print(f"  📍 จังหวัดเริ่มต้น : {DEFAULT_CITY}")
    print(f"  👤 เจ้าของ bot    : {'ตั้งแล้ว ✅' if MY_LINE_USER_ID else 'ยังไม่ตั้ง — พิมพ์ id ใน LINE'}")
    print(f"  🔔 Monitor        : {'เปิด' if ENABLE_MONITOR else 'ปิด'}")
    print(f"  🌐 รันที่          : http://{HOST}:{PORT}")
    print(f"  🔗 Webhook        : http://{HOST}:{PORT}/webhook")
    print()
    print("  Tunnel (เลือกอย่างใดอย่างหนึ่ง):")
    print(f"    ngrok http {PORT}")
    print(f"    cloudflared tunnel --url http://{HOST}:{PORT}")
    print()


missing = ensure_ready()
print_banner(missing)
if missing:
    sys.exit(1)

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
db = get_db()
broadcast_svc = BroadcastService(line_bot_api, db)


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@app.route("/")
def index():
    stats = db.get_stats()
    return jsonify({
        "bot": "CBS Personal",
        "status": "running",
        "users": stats["total_users"],
        "owner_set": bool(MY_LINE_USER_ID),
    })


@handler.add(MessageEvent, message=TextMessage)
def on_text_message(event):
    user_id = event.source.user_id
    text = event.message.text
    try:
        reply = handle_message(user_id, text, db, broadcast_svc)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply),
        )
    except Exception as exc:
        logger.exception("Error: %s", exc)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ เกิดข้อผิดพลาด ลองใหม่อีกครั้ง"),
        )


def start_monitor():
    MonitorService(line_bot_api, db).run_loop()


if ENABLE_MONITOR:
    threading.Thread(target=start_monitor, daemon=True).start()
    logger.info("Monitor เปิด — เช็คทุก %s วินาที", os.getenv("MONITOR_INTERVAL_SEC", "600"))

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
