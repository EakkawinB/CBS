"""SQLite + เข้ารหัส user_id และ broadcast log"""

import hashlib
import hmac
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from config import DB_PATH, ENCRYPTION_KEY, DEFAULT_CITY
from crypto_utils import CryptoManager, get_crypto


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, db_path: str = DB_PATH, crypto: CryptoManager | None = None):
        self.db_path = db_path
        self.crypto = crypto or get_crypto()
        self._lookup_key = ENCRYPTION_KEY.encode() or b"cbs-default-key"
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        with self.connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id_hash TEXT NOT NULL UNIQUE,
                    user_id_enc TEXT NOT NULL,
                    city TEXT DEFAULT 'กรุงเทพ',
                    alerts_enabled INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS broadcast_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id_hash TEXT NOT NULL,
                    admin_id_enc TEXT NOT NULL,
                    message_enc TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_city TEXT,
                    sent_count INTEGER DEFAULT 0,
                    fail_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS system_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_users_city ON users(city);
                CREATE INDEX IF NOT EXISTS idx_users_alerts ON users(alerts_enabled);
            """)

    def _uid_hash(self, user_id: str) -> str:
        """Hash คงที่สำหรับ lookup (Fernet encrypt ไม่ deterministic)"""
        return hmac.new(
            self._lookup_key, user_id.encode(), hashlib.sha256
        ).hexdigest()

    def _enc_uid(self, user_id: str) -> str:
        return self.crypto.encrypt(user_id)

    def _dec_uid(self, user_id_enc: str) -> str:
        return self.crypto.decrypt(user_id_enc)

    def upsert_user(self, user_id: str, city: str | None = None) -> None:
        uid_hash = self._uid_hash(user_id)
        enc = self._enc_uid(user_id)
        now = _now()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE user_id_hash = ?", (uid_hash,)
            ).fetchone()
            if row:
                if city:
                    conn.execute(
                        "UPDATE users SET city=?, updated_at=? WHERE user_id_hash=?",
                        (city, now, uid_hash),
                    )
            else:
                conn.execute(
                    """INSERT INTO users
                       (user_id_hash, user_id_enc, city, alerts_enabled, created_at, updated_at)
                       VALUES (?, ?, ?, 1, ?, ?)""",
                    (uid_hash, enc, city or DEFAULT_CITY, now, now),
                )

    def set_city(self, user_id: str, city: str) -> bool:
        uid_hash = self._uid_hash(user_id)
        with self.connect() as conn:
            cur = conn.execute(
                "UPDATE users SET city=?, updated_at=? WHERE user_id_hash=?",
                (city, _now(), uid_hash),
            )
            return cur.rowcount > 0

    def get_user(self, user_id: str) -> dict | None:
        uid_hash = self._uid_hash(user_id)
        with self.connect() as conn:
            row = conn.execute(
                "SELECT city, alerts_enabled FROM users WHERE user_id_hash=?",
                (uid_hash,),
            ).fetchone()
        if not row:
            return None
        return {"city": row["city"], "alerts_enabled": bool(row["alerts_enabled"])}

    def set_alerts(self, user_id: str, enabled: bool) -> None:
        uid_hash = self._uid_hash(user_id)
        with self.connect() as conn:
            conn.execute(
                "UPDATE users SET alerts_enabled=?, updated_at=? WHERE user_id_hash=?",
                (1 if enabled else 0, _now(), uid_hash),
            )

    def get_subscribers(self, city: str | None = None, alerts_only: bool = True) -> list[dict]:
        query = "SELECT user_id_enc, city, alerts_enabled FROM users WHERE 1=1"
        params: list = []
        if alerts_only:
            query += " AND alerts_enabled = 1"
        if city:
            query += " AND city = ?"
            params.append(city)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "user_id": self._dec_uid(r["user_id_enc"]),
                "city": r["city"],
                "alerts_enabled": bool(r["alerts_enabled"]),
            }
            for r in rows
        ]

    def get_stats(self) -> dict:
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
            active = conn.execute(
                "SELECT COUNT(*) AS c FROM users WHERE alerts_enabled=1"
            ).fetchone()["c"]
            broadcasts = conn.execute(
                "SELECT COUNT(*) AS c FROM broadcast_logs"
            ).fetchone()["c"]
            by_city = conn.execute(
                "SELECT city, COUNT(*) AS c FROM users GROUP BY city ORDER BY c DESC LIMIT 10"
            ).fetchall()
        return {
            "total_users": total,
            "active_subscribers": active,
            "total_broadcasts": broadcasts,
            "top_cities": [(r["city"], r["c"]) for r in by_city],
        }

    def log_broadcast(
        self,
        admin_id: str,
        message: str,
        target_type: str,
        target_city: str | None,
        sent_count: int,
        fail_count: int,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """INSERT INTO broadcast_logs
                   (admin_id_hash, admin_id_enc, message_enc, target_type, target_city,
                    sent_count, fail_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._uid_hash(admin_id),
                    self._enc_uid(admin_id),
                    self.crypto.encrypt(message),
                    target_type,
                    target_city,
                    sent_count,
                    fail_count,
                    _now(),
                ),
            )
            return cur.lastrowid


_db: Database | None = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
