"""CellBoardCast — ส่งข้อความ broadcast ไปยัง subscriber"""

import logging
import time

from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

from config import BROADCAST_DELAY_SEC, MAX_BROADCAST_LEN
from database import Database

logger = logging.getLogger(__name__)


class BroadcastService:
    PREFIX = "📢"

    def __init__(self, line_api: LineBotApi, db: Database):
        self.line_api = line_api
        self.db = db

    def send(
        self,
        admin_id: str,
        message: str,
        target_type: str = "all",
        target_city: str | None = None,
    ) -> dict:
        message = message.strip()
        if not message:
            return {"ok": False, "error": "ข้อความว่างเปล่า"}
        if len(message) > MAX_BROADCAST_LEN:
            return {"ok": False, "error": f"ข้อความยาวเกิน {MAX_BROADCAST_LEN} ตัวอักษร"}

        subscribers = self.db.get_subscribers(
            city=target_city if target_type == "city" else None,
            alerts_only=False,
        )
        if not subscribers:
            return {"ok": False, "error": "ไม่มีผู้รับในกลุ่มที่เลือก"}

        full_text = f"{self.PREFIX}\n{message}"
        sent, failed = 0, 0
        errors: list[str] = []

        for sub in subscribers:
            try:
                self.line_api.push_message(
                    sub["user_id"],
                    TextSendMessage(text=full_text),
                )
                sent += 1
                time.sleep(BROADCAST_DELAY_SEC)
            except LineBotApiError as exc:
                failed += 1
                errors.append(f"{sub['user_id'][:8]}…: {exc.message}")
                logger.warning("Broadcast fail %s: %s", sub["user_id"][:8], exc.message)

        log_id = self.db.log_broadcast(
            admin_id=admin_id,
            message=message,
            target_type=target_type,
            target_city=target_city,
            sent_count=sent,
            fail_count=failed,
        )

        return {
            "ok": True,
            "log_id": log_id,
            "sent": sent,
            "failed": failed,
            "total": len(subscribers),
            "errors": errors[:5],
        }
