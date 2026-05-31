"""คำสั่ง LINE Bot — โหมดใช้ส่วนตัว"""

from config import DEFAULT_CITY, MAX_BROADCAST_LEN, MY_LINE_USER_ID, is_owner
from cities import CITIES
from database import Database
from services.broadcast import BroadcastService

HELP_TEXT = """📋 คำสั่ง CBS Bot

🔹 ตั้งจังหวัด [ชื่อ] — ตั้งพื้นที่แจ้งเตือน
🔹 สถานะ — ดูการตั้งค่า
🔹 เปิดแจ้งเตือน / ปิดแจ้งเตือน
🔹 id — ดู LINE User ID (ใส่ใน .env)
🔹 ช่วยเหลือ — แสดงคำสั่งนี้"""

OWNER_HELP = """
🔐 คำสั่งเจ้าของ bot
🔸 ส่ง [ข้อความ] — ส่งข้อความถึงทุกคนที่ลงทะเบียน
🔸 ส่ง [จังหวัด] [ข้อความ] — ส่งเฉพาะจังหวัด
🔸 สถิติ — ดูข้อมูลระบบ"""


def handle_message(
    user_id: str,
    text: str,
    db: Database,
    broadcast_svc: BroadcastService,
) -> str:
    text = text.strip()
    db.upsert_user(user_id)

    # ---- คำสั่งเจ้าของ ----
    if is_owner(user_id):
        owner_reply = _handle_owner(user_id, text, db, broadcast_svc)
        if owner_reply is not None:
            return owner_reply

    # ---- คำสั่งทั่วไป ----
    if text.lower() in ("id", "ไอดี", "myid"):
        return _handle_show_id(user_id)

    if text.startswith("ตั้งจังหวัด "):
        city = text.replace("ตั้งจังหวัด ", "", 1).strip()
        if city in CITIES:
            db.set_city(user_id, city)
            return f"✅ ตั้งจังหวัดเป็น '{city}' แล้ว"
        return "❌ ไม่พบจังหวัด\nลอง: ตั้งจังหวัด เชียงใหม่"

    if text == "สถานะ":
        user = db.get_user(user_id)
        if not user:
            return "❌ ยังไม่มีข้อมูล ลองพิมพ์ ช่วยเหลือ"
        alert = "เปิด ✅" if user["alerts_enabled"] else "ปิด ❌"
        owner_tag = " (เจ้าของ bot)" if is_owner(user_id) else ""
        return (
            f"🤖 CBS Bot ทำงานปกติ{owner_tag}\n"
            f"📍 จังหวัด: {user['city']}\n"
            f"🔔 แจ้งเตือนอัตโนมัติ: {alert}"
        )

    if text in ("เปิดแจ้งเตือน", "เปิด"):
        db.set_alerts(user_id, True)
        return "✅ เปิดแจ้งเตือนแล้ว"

    if text in ("ปิดแจ้งเตือน", "ปิด"):
        db.set_alerts(user_id, False)
        return "🔕 ปิดแจ้งเตือนแล้ว"

    if text in ("ช่วยเหลือ", "help"):
        msg = HELP_TEXT
        if is_owner(user_id):
            msg += OWNER_HELP
        elif not MY_LINE_USER_ID:
            msg += "\n\n💡 ยังไม่ได้ตั้ง MY_LINE_USER_ID\nพิมพ์ id แล้วใส่ใน .env"
        return msg

    return (
        f"สวัสดี 👋 ยินดีต้อนรับ CBS Bot\n"
        f"📍 จังหวัดเริ่มต้น: {DEFAULT_CITY}\n"
        f"พิมพ์ ช่วยเหลือ เพื่อดูคำสั่ง"
    )


def _handle_show_id(user_id: str) -> str:
    lines = [
        f"🆔 LINE User ID ของคุณ:\n{user_id}",
        "",
        "นำไปใส่ใน .env:",
        f"MY_LINE_USER_ID={user_id}",
        "",
        "แล้วรีสตาร์ท bot (Ctrl+C → run.ps1)",
    ]
    if is_owner(user_id):
        lines.insert(1, "✅ คุณเป็นเจ้าของ bot แล้ว")
    return "\n".join(lines)


def _handle_owner(
    user_id: str,
    text: str,
    db: Database,
    broadcast_svc: BroadcastService,
) -> str | None:
    if text == "สถิติ":
        stats = db.get_stats()
        top = "\n".join(f"  • {c}: {n}" for c, n in stats["top_cities"][:5])
        return (
            f"📊 สถิติ\n"
            f"👥 ผู้ใช้: {stats['total_users']}\n"
            f"🔔 เปิดแจ้งเตือน: {stats['active_subscribers']}\n"
            f"📢 ส่ง broadcast: {stats['total_broadcasts']} ครั้ง\n"
            f"🏙️ จังหวัดยอดนิยม:\n{top or '  (ยังไม่มี)'}"
        )

    if text.startswith("ส่ง ") or text.startswith("broadcast "):
        prefix = "ส่ง " if text.startswith("ส่ง ") else "broadcast "
        return _handle_send(user_id, text[len(prefix):].strip(), broadcast_svc)

    return None


def _handle_send(user_id: str, body: str, broadcast_svc: BroadcastService) -> str:
    parts = body.split(" ", 1)
    target_type = "all"
    target_city = None
    message = body

    if len(parts) == 2 and parts[0] in CITIES:
        target_type = "city"
        target_city = parts[0]
        message = parts[1].strip()

    if not message:
        return "❌ ตัวอย่าง: ส่ง สวัสดีครับ"
    if len(message) > MAX_BROADCAST_LEN:
        return f"❌ ข้อความยาวเกิน {MAX_BROADCAST_LEN} ตัวอักษร"

    result = broadcast_svc.send(
        admin_id=user_id,
        message=message,
        target_type=target_type,
        target_city=target_city,
    )

    if not result["ok"]:
        return f"❌ ส่งไม่สำเร็จ: {result['error']}"

    scope = target_city if target_type == "city" else "ทุกคน"
    return (
        f"✅ ส่งแล้ว!\n"
        f"🎯 ถึง: {scope}\n"
        f"📤 สำเร็จ: {result['sent']}/{result['total']}"
    )
