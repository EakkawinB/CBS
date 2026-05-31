"""สร้าง ENCRYPTION_KEY — โหมดส่วนตัวสร้างอัตโนมัติแล้ว ไม่ต้องรันเอง"""

from config import LOCAL_KEY_FILE, _load_or_create_encryption_key

if __name__ == "__main__":
    key = _load_or_create_encryption_key()
    print("ENCRYPTION_KEY (เก็บอัตโนมัติแล้ว):")
    print(f"  ไฟล์: {LOCAL_KEY_FILE}")
    print(f"  ค่า:  {key[:12]}...")
