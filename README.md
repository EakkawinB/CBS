# CBS Bot

LINE Bot ส่วนตัวสำหรับแจ้งเตือนแผ่นดินไหว/ฝน และส่งข้อความ broadcast — ออกแบบให้รันบนเครื่องตัวเองได้ง่าย

**Repository:** [github.com/EakkawinB/CBS](https://github.com/EakkawinB/CBS)

---

## ฟีเจอร์

- **แจ้งเตือนแผ่นดินไหว** — ดึงข้อมูลจาก USGS แจ้งเมื่อใกล้จังหวัดที่ตั้งไว้
- **แจ้งเตือนฝน** — ใช้ OpenWeather API (ตั้งค่า optional)
- **CellBoardCast** — เจ้าของ bot ส่งข้อความถึงผู้ใช้ทั้งหมดหรือเฉพาะจังหวัด
- **77 จังหวัด** — รองรับชื่อจังหวัดภาษาไทย
- **เข้ารหัสข้อมูล** — LINE User ID และ broadcast log ถูกเข้ารหัสใน SQLite
- **โหมดส่วนตัว** — ตั้งค่าน้อย รันบนเครื่อง + ngrok/cloudflared

---

## โครงสร้างโปรเจกต์

```
CBS/
├── main.py              # Flask webhook + background monitor
├── config.py            # โหลดค่าจาก .env
├── handlers.py          # คำสั่ง LINE
├── database.py          # SQLite + encryption
├── crypto_utils.py      # Fernet encryption
├── cities.py            # 77 จังหวัด + พิกัด
├── setup.py             # ตั้งค่าครั้งแรก
├── run.ps1              # รัน bot (Windows)
├── services/
│   ├── broadcast.py     # ส่งข้อความ broadcast
│   └── monitor.py       # เช็คแผ่นดินไหว/ฝน
├── .env.example         # ตัวอย่าง config
└── requirements.txt
```

---

## ความต้องการของระบบ

- Python 3.10+
- บัญชี [LINE Developers](https://developers.line.biz/console/)
- (แนะนำ) [ngrok](https://ngrok.com/) หรือ [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) สำหรับ webhook

---

## วิธีติดตั้ง

### 1. Clone โปรเจกต์

```bash
git clone https://github.com/EakkawinB/CBS.git
cd CBS
```

### 2. ตั้งค่าครั้งแรก

```powershell
python setup.py
```

กรอกค่าจาก LINE Developers Console:

| ตัวแปร | ที่มา |
|--------|-------|
| `CHANNEL_ACCESS_TOKEN` | Messaging API → Channel access token |
| `CHANNEL_SECRET` | Basic settings → Channel secret |

### 3. รัน bot

```powershell
.\run.ps1
```

หรือ

```bash
pip install -r requirements.txt
python main.py
```

### 4. เปิด Tunnel

```powershell
ngrok http 5000
```

หรือ

```powershell
cloudflared tunnel --url http://127.0.0.1:5000
```

### 5. ตั้ง Webhook ใน LINE Console

1. ไปที่ Messaging API → **Webhook settings**
2. ใส่ URL: `https://xxxx.ngrok-free.app/webhook`
3. เปิด **Use webhook**
4. ปิด **Auto-reply messages** และ **Greeting messages**

### 6. ลงทะเบียนเป็นเจ้าของ bot

1. เปิด LINE แล้วพิมพ์ `id` หา bot
2. Copy User ID ใส่ใน `.env`:

```env
MY_LINE_USER_ID=Uxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

3. รีสตาร์ท bot

---

## คำสั่งใน LINE

### ผู้ใช้ทั่วไป

| คำสั่ง | คำอธิบาย |
|--------|----------|
| `ตั้งจังหวัด เชียงใหม่` | ตั้งพื้นที่แจ้งเตือน |
| `สถานะ` | ดูการตั้งค่าปัจจุบัน |
| `เปิด` / `ปิด` | เปิด/ปิดแจ้งเตือนอัตโนมัติ |
| `id` | ดู LINE User ID |
| `ช่วยเหลือ` | แสดงคำสั่งทั้งหมด |

### เจ้าของ bot (`MY_LINE_USER_ID`)

| คำสั่ง | คำอธิบาย |
|--------|----------|
| `ส่ง สวัสดีครับ` | broadcast ถึงทุกคน |
| `ส่ง เชียงใหม่ ฝนตกแล้ว` | broadcast เฉพาะจังหวัด |
| `สถิติ` | ดูจำนวนผู้ใช้และ broadcast log |

---

## การตั้งค่า (.env)

```env
# จำเป็น
CHANNEL_ACCESS_TOKEN=
CHANNEL_SECRET=
MY_LINE_USER_ID=

# ส่วนตัว
DEFAULT_CITY=กรุงเทพ
ENABLE_MONITOR=true
PORT=5000

# ไม่บังคับ — แจ้งเตือนฝน
OPENWEATHER_API_KEY=
```

| ตัวแปร | ค่าเริ่มต้น | คำอธิบาย |
|--------|-------------|----------|
| `DEFAULT_CITY` | กรุงเทพ | จังหวัดเริ่มต้นสำหรับผู้ใช้ใหม่ |
| `ENABLE_MONITOR` | true | เปิด/ปิดแจ้งเตือนอัตโนมัติ |
| `PORT` | 5000 | พอร์ตที่ bot รัน |
| `MONITOR_INTERVAL_SEC` | 600 | ช่วงเช็คแผ่นดินไหว/ฝน (วินาที) |
| `EARTHQUAKE_MIN_MAG` | 4.0 | ขนาดแผ่นดินไหวขั้นต่ำที่แจ้ง |
| `EARTHQUAKE_RADIUS_KM` | 1500 | ระยะทางสูงสุดจากจังหวัด (กม.) |

> `ENCRYPTION_KEY` สร้างอัตโนมัติที่ `data/.local_key` — ไม่ต้องใส่เอง

---

## ความปลอดภัย

- **อย่า commit `.env`** — มี token และ secret ของ LINE
- **อย่าแชร์ `data/.local_key`** — คีย์เข้ารหัสข้อมูลใน DB
- **อย่าแชร์ `data/cbs.db`** — มี user_id ที่เข้ารหัสแล้ว
- Token LINE ควร rotate ทันทีหากรั่วไหล

ไฟล์ที่ git ignore แล้ว:

```
.env
data/
*.db
__pycache__/
```

---

## API Endpoints

| Path | Method | คำอธิบาย |
|------|--------|----------|
| `/webhook` | POST | LINE webhook |
| `/` | GET | สถานะ bot (JSON) |
| `/health` | GET | health check |

---

## Deploy บน Cloud (optional)

สำหรับรันบน Render, Railway ฯลฯ ตั้ง environment variables เหมือนใน `.env` แล้วใช้:

```bash
gunicorn main:app --bind 0.0.0.0:$PORT
```

---

## License

MIT — ใช้งานและแก้ไขได้ตามต้องการ

---

## ผู้พัฒนา

[EakkawinB](https://github.com/EakkawinB)
