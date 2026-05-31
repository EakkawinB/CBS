"""เข้ารหัสข้อมูลสำคัญด้วย Fernet (AES-128-CBC + HMAC)"""

import base64
import hashlib
import hmac
import secrets

from cryptography.fernet import Fernet, InvalidToken

from config import ENCRYPTION_KEY


class CryptoManager:
    def __init__(self, key: str | None = None):
        raw = (key or ENCRYPTION_KEY).encode()
        if not raw:
            raise ValueError("ENCRYPTION_KEY ไม่ได้ตั้งค่า")
        # รองรับ key ที่เป็น Fernet key โดยตรง หรือ passphrase ธรรมดา
        try:
            self._fernet = Fernet(raw)
        except Exception:
            derived = base64.urlsafe_b64encode(
                hashlib.sha256(raw).digest()
            )
            self._fernet = Fernet(derived)

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise ValueError("ถอดรหัสไม่สำเร็จ — key ไม่ตรงหรือข้อมูลเสียหาย") from exc

    @staticmethod
    def hash_pin(pin: str, salt: bytes | None = None) -> str:
        """เก็บ PIN แบบ salted SHA-256"""
        if salt is None:
            salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 120_000)
        return f"{salt.hex()}:{digest.hex()}"

    @staticmethod
    def verify_pin(pin: str, stored: str) -> bool:
        try:
            salt_hex, digest_hex = stored.split(":", 1)
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 120_000)
            return hmac.compare_digest(actual, expected)
        except (ValueError, AttributeError):
            return False


_crypto: CryptoManager | None = None


def get_crypto() -> CryptoManager:
    global _crypto
    if _crypto is None:
        _crypto = CryptoManager()
    return _crypto
