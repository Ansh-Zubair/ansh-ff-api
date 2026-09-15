```markdown
# 🐱 ANSH FF INFO API

<div align="center">

![Version](https://img.shields.io/badge/version-12.0-blue.svg?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.9+-yellow.svg?style=for-the-badge)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-red.svg?style=for-the-badge)

**Free Fire Player Information API**
*Made with ❤️ by ANSH*

[Features](#-features) · [Endpoints](#-api-endpoints) · [Deploy](#-deployment) · [Usage](#-usage-examples)

</div>

---

## 📖 About

ANSH FF INFO API is a **Free Fire player information API** that provides detailed data about any player using just their UID. It fetches **real-time data** from Free Fire servers using Guest accounts, JWT authentication, and Protobuf decoding.

**No login required for end users** — just provide a UID and get instant results.

---

## ✨ Features

- ✅ **Player Info** — Name, level, exp, likes, bio, region
- ✅ **Guild Info** — Guild name, level, members, leader details
- ✅ **Ban Check** — Check if account is active or banned
- ✅ **Equipped Items** — Avatar, banner, badge, title, bundle IDs
- ✅ **Account Age** — Creation date, last login, account age
- ✅ **Likes Progress** — Smart milestone tracking (+100 steps)
- ✅ **Multi-Region** — 13 regions supported
- ✅ **Readable Unicode** — No `\uXXXX` escapes, proper emojis & special chars
- ✅ **Account Rotation** — Auto-rotate through 100+ guest accounts
- ✅ **Clean Bio** — Hex decode → readable text
- ✅ **Fast Response** — Average 5-8 seconds per request
- ✅ **REST API** — Simple JSON responses
- ✅ **Web Interface** — Built-in website with popup support
- ✅ **Vercel Ready** — One-click deployment

---

## 🌍 Supported Regions

| Code | Region | Code | Region |
|------|--------|------|--------|
| `IND` | 🇮🇳 India | `TH` | 🇹🇭 Thailand |
| `VN` | 🇻🇳 Vietnam | `ME` | 🇦🇪 Middle East |
| `BR` | 🇧🇷 Brazil | `BD` | 🇧🇩 Bangladesh |
| `SG` | 🇸🇬 Singapore | `ID` | 🇮🇩 Indonesia |
| `MY` | 🇲🇾 Malaysia | `PK` | 🇵🇰 Pakistan |
| `EG` | 🇪🇬 Egypt | `RU` | 🇷🇺 Russia |
| `US` | 🇺🇸 United States | | |

---

## 🔌 API Endpoints

### **Base URL**

```
Local:  http://127.0.0.1:8000
Vercel: https://ansh-ff-api.vercel.app
```

### **1. Player Info**

```http
GET /info?uid=<uid>&region=<region>
```

**Parameters:**

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `uid` | ✅ Yes | Player UID (numeric) | `9065125195` |
| `region` | ❌ Optional | Region code (default: `IND`) | `IND` |

**Example:**

```bash
curl "https://ansh-ff-api.vercel.app/info?uid=9065125195"
```

**Response:**

```json
{
  "status": "success",
  "uid": "9065125195",
  "nickname": "Kɪɴɢ Aɴsʜ 모",
  "level": 34,
  "exp": 69593,
  "likes": 829,
  "likes_progress": {
    "current": 829,
    "next_milestone": 900,
    "needed": 71,
    "progress_percentage": 29.0,
    "formatted": "829 / 900 (71 more needed)"
  },
  "region": "IND",
  "bio": "[C][B][00FFFF] YT-@ANSHTECHIE | IG-@hiezp",
  "avatar_id": 902052018,
  "banner_id": 306,
  "badge": 1549,
  "title_id": 1001000100,
  "bundle_id": 904053008,
  "created_date": "25 March 2024",
  "last_login": "13 September 2026, 23:19",
  "account_age_days": 902,
  "account_age_string": "2 years 5 months",
  "honor_score": 91,
  "guild": {
    "id": "3045688667",
    "name": "AɴsʜɢᴀᴍɪɴɢAɢ",
    "level": 1,
    "members": 46,
    "max_members": 55,
    "leader": {
      "uid": "8225139205",
      "nickname": "ᴀɴꜱʜ ɢᴍʀ ☯︎",
      "level": 42,
      "exp": 143176,
      "likes": 341,
      "avatar_id": 902042025,
      "banner_id": 306,
      "badge": 1570,
      "bundle_id": 904031002
    }
  },
  "powered_by": "ANSH"
}
```

---

### **2. Guild Info**

```http
GET /guild?uid=<uid>&region=<region>
```

**Parameters:**

| Param | Required | Description | Example |
|-------|----------|-------------|---------|
| `uid` | ✅ Yes | Player UID (numeric) | `9065125195` |
| `region` | ❌ Optional | Region code (default: `IND`) | `IND` |

**Example:**

```bash
curl "https://ansh-ff-api.vercel.app/guild?uid=9065125195"
```

**Response:**

```json
{
  "status": "success",
  "guild": {
    "id": "3045688667",
    "name": "AɴsʜɢᴀᴍɪɴɢAɢ",
    "level": 1,
    "members": 46,
    "max_members": 55,
    "leader": {
      "uid": "8225139205",
      "nickname": "ᴀɴꜱʜ ɢᴍʀ ☯︎",
      "level": 42,
      "exp": 143176,
      "likes": 341,
      "avatar_id": 902042025,
      "banner_id": 306,
      "badge": 1570,
      "title_id": 1001000100,
      "bundle_id": 904031002
    }
  },
  "powered_by": "ANSH"
}
```

---

### **3. Ban Check**

```http
GET /ban?uid=<uid>&region=<region>
```

**Example:**

```bash
curl "https://ansh-ff-api.vercel.app/ban?uid=9065125195"
```

**Response (Active):**

```json
{
  "status": "success",
  "uid": "9065125195",
  "banned": false,
  "account_status": "ACTIVE",
  "region": "IND",
  "nickname": "Kɪɴɢ Aɴsʜ 모",
  "level": 34,
  "likes": 829,
  "checked_at": "2026-09-15 00:15:30",
  "powered_by": "ANSH"
}
```

**Response (Banned):**

```json
{
  "status": "success",
  "uid": "9065125195",
  "banned": true,
  "account_status": "BANNED_OR_DELETED",
  "region": "IND",
  "checked_at": "2026-09-15 00:15:30",
  "powered_by": "ANSH"
}
```

---

### **4. Health Check**

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "accounts": 132,
  "time": "2026-09-15 00:15:30"
}
```

---

### **5. API Info**

```http
GET /api
```

**Response:**

```json
{
  "status": "success",
  "api": "ANSH FF INFO API",
  "version": "12.0",
  "accounts": 132,
  "powered_by": "ANSH",
  "endpoints": [
    "/info?uid=<uid>&region=IND",
    "/guild?uid=<uid>&region=IND",
    "/ban?uid=<uid>&region=IND",
    "/health"
  ],
  "regions": ["IND", "TH", "VN", "ME", "BR", "BD", "SG", "ID", "MY", "PK", "EG", "RU", "US"]
}
```

---

## 🚀 Deployment

### **Local Setup (Termux / Linux)**

#### **1. Clone or Download**

```bash
git clone https://github.com/YOUR_USERNAME/ansh-ff-api.git
cd ansh-ff-api
```

#### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

#### **3. Add Guest Accounts**

Create `accounts.json`:

```json
[
  {"uid": "7566323842", "password": "ANSH_8QVN"},
  {"uid": "7566323874", "password": "ANSH_5GLF"}
]
```

**⚠️ Minimum 10 accounts recommended for smooth rotation.**

#### **4. Run Server**

```bash
python main.py
```

**Output:**

```
╔═══════════════════════════════════════════════╗
║  🐱 ANSH FF INFO API v12.0 FIXED              ║
║  Made with ❤️  by ANSH                        ║
╚═══════════════════════════════════════════════╝

✅ Loaded 132 guest accounts
🚀 Server starting on http://0.0.0.0:8000
```

#### **5. Test**

```bash
curl "http://localhost:8000/info?uid=9065125195"
```

---

### **Vercel Deployment**

#### **1. Push to GitHub**

```bash
git init
git add .
git commit -m "ANSH FF INFO API v12.0"
git remote add origin https://github.com/YOUR_USERNAME/ansh-ff-api.git
git branch -M main
git push -u origin main
```

#### **2. Deploy on Vercel**

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click **"Add New Project"**
4. Import **ansh-ff-api** repository
5. Framework Preset: **Other**
6. Click **Deploy**

**Your API will be live at:**

```
https://ansh-ff-api.vercel.app
```

---

## 📁 Project Structure

```
ansh-ff-api/
├── main.py                  # Flask API server
├── index.html               # Web interface
├── accounts.json            # Guest accounts (UID + Password)
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel deployment config
├── README.md                # Documentation
└── Pb2/                     # Protobuf definitions
    ├── __init__.py
    ├── DEcwHisPErMsG_pb2.py
    ├── Fo_pb2.py
    ├── GenWhisperMsg_pb2.py
    ├── kyro_title_pb2.py
    ├── MajoRLoGinrEq_pb2.py
    ├── MajoRLoGinrEs_pb2.py
    ├── PorTs_pb2.py
    ├── room_join_pb2.py
    ├── sQ_pb2.py
    └── Team_msg_pb2.py
```

---

## 🎯 Usage Examples

### **Python**

```python
import requests

def get_player_info(uid):
    url = f"https://ansh-ff-api.vercel.app/info?uid={uid}"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "success":
        print(f"Name: {data['nickname']}")
        print(f"Level: {data['level']}")
        print(f"Likes: {data['likes']}")
        print(f"Guild: {data['guild']['name']}")
    else:
        print(f"Error: {data['message']}")

get_player_info("9065125195")
```

### **JavaScript**

```javascript
async function getPlayerInfo(uid) {
  const res = await fetch(`https://ansh-ff-api.vercel.app/info?uid=${uid}`);
  const data = await res.json();
  
  if (data.status === "success") {
    console.log(`Name: ${data.nickname}`);
    console.log(`Level: ${data.level}`);
    console.log(`Likes: ${data.likes}`);
  } else {
    console.error(`Error: ${data.message}`);
  }
}

getPlayerInfo("9065125195");
```

### **Telegram Bot (Python)**

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp

API_URL = "https://ansh-ff-api.vercel.app"

async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = context.args[0] if context.args else None
    if not uid:
        await update.message.reply_text("Usage: /info <uid>")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/info?uid={uid}") as r:
            data = await r.json()
    
    if data["status"] == "success":
        msg = f"📛 {data['nickname']}\n🏆 Level: {data['level']}\n❤️ Likes: {data['likes']}"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ Player not found")

app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("info", info_cmd))
app.run_polling()
```

---

## ⚠️ Error Responses

| Status Code | Meaning |
|-------------|---------|
| `200` | Success |
| `400` | Invalid/missing UID |
| `404` | Player/Guild not found |
| `500` | Server error (OAuth/JWT) |
| `503` | No accounts loaded |

**Error format:**

```json
{
  "status": "error",
  "message": "Player not found",
  "powered_by": "ANSH"
}
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Avg Response Time** | 5-8 seconds |
| **Account Rotation** | Auto |
| **Concurrent Requests** | 100+ |
| **Uptime** | 24/7 |
| **Rate Limit** | None |

---

## 🔒 Security

- ✅ **No authentication required** for end users
- ✅ **Guest account rotation** protects primary accounts
- ✅ **AES encrypted** requests to Free Fire servers
- ✅ **JWT authentication** for API calls
- ✅ **HTTPS only** in production

---

## 📋 Requirements

```
Python >= 3.9
flask==3.0.0
aiohttp==3.9.1
pycryptodome==3.19.0
protobuf>=6.33.1
```

---

## 🎨 Web Interface

Open in browser:

```
http://localhost:8000
```

**Features:**

- 🔍 Player info search
- 🏰 Guild info search
- 🚫 Ban check
- 💝 Support popup with UID copy
- 📢 Notice banner (IND server only)
- 🌈 Animated loading screen
- 📱 Mobile responsive

---

## 📢 Notice

```
We haven't added other server services yet.
Currently supporting: IND server only.

⏳ Other regions will be added:
   18/09/2026 → 27/09/2026
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

MIT License — Free to use for educational and personal purposes.

---

## 👨‍💻 Author

**ANSH**

- 🐱 Developer of ANSH FF INFO API
- 📱 Telegram: [@AnshFFBot](https://t.me/AnshFFBot)
- 📷 Instagram: [@hiezp](https://instagram.com/hiezp)
- ▶️ YouTube: [@ANSHTECHIE](https://youtube.com/@ANSHTECHIE)

---

## 💝 Support

If this project helped you, please support:

**UID 1:** `9065125195`
**UID 2:** `14552958340`

*Send likes & friend requests!*

---

<div align="center">

**⭐ Star this repo if you found it useful! ⭐**

Made with ❤️ by **ANSH**

</div>
```
