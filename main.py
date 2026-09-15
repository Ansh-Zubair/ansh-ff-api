#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════
#       ANSH FF INFO API v12.0 - FINAL FIXED
#       Info · Guild · Ban · Vercel Ready
#       Made with ❤️  by ANSH
# ═══════════════════════════════════════════════════════════════════

import os
import sys
import json
import ssl
import base64
import asyncio
import re
import traceback
from datetime import datetime

from flask import Flask, Response, request, send_from_directory
import aiohttp

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    from Pb2 import MajoRLoGinrEq_pb2, MajoRLoGinrEs_pb2
except ImportError as e:
    print(f"❌ Pb2/Crypto missing: {e}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════
#       CONFIG
# ═══════════════════════════════════════════════════════════════════
API_NAME = "ANSH FF INFO API"
API_VERSION = "12.0"
POWERED_BY = "ANSH"

CLIENT_ID = "100067"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ggblueshark.com/MajorLogin"

KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

REGION_URLS = {
    "IND": "https://client.ind.freefiremobile.com",
    "TH":  "https://client.th.freefiremobile.com",
    "VN":  "https://client.vn.freefiremobile.com",
    "ME":  "https://client.me.freefiremobile.com",
    "BR":  "https://client.br.freefiremobile.com",
    "BD":  "https://client.bd.freefiremobile.com",
    "SG":  "https://client.sg.freefiremobile.com",
    "ID":  "https://client.id.freefiremobile.com",
    "MY":  "https://client.my.freefiremobile.com",
    "PK":  "https://client.pk.freefiremobile.com",
    "EG":  "https://client.eg.freefiremobile.com",
    "RU":  "https://client.ru.freefiremobile.com",
    "US":  "https://client.us.freefiremobile.com",
}

ACCOUNTS = []
CURRENT_INDEX = 0


# ═══════════════════════════════════════════════════════════════════
#       JSON RESPONSE
# ═══════════════════════════════════════════════════════════════════
def json_response(data, status=200):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status,
        mimetype='application/json; charset=utf-8'
    )


# ═══════════════════════════════════════════════════════════════════
#       LOAD ACCOUNTS
# ═══════════════════════════════════════════════════════════════════
def load_accounts():
    global ACCOUNTS
    path = "accounts.json"
    if not os.path.isfile(path):
        print(f"⚠️  {path} not found")
        ACCOUNTS = []
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        accounts = []
        if isinstance(data, list):
            for a in data:
                if isinstance(a, dict):
                    uid = a.get("uid")
                    pwd = a.get("password")
                    if uid and pwd:
                        accounts.append({"uid": str(uid), "password": str(pwd)})
        ACCOUNTS = accounts
        print(f"✅ Loaded {len(ACCOUNTS)} guest accounts")
    except Exception as e:
        print(f"❌ Account load error: {e}")
        ACCOUNTS = []


def get_next_account():
    global CURRENT_INDEX
    if not ACCOUNTS:
        return None
    acc = ACCOUNTS[CURRENT_INDEX % len(ACCOUNTS)]
    CURRENT_INDEX += 1
    return acc


def get_region_from_jwt(jwt):
    try:
        parts = jwt.split(".")
        if len(parts) != 3:
            return "IND"
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        region = (data.get("noti_region") or
                  data.get("country_code") or
                  data.get("lock_region") or
                  "IND").upper()
        return region
    except Exception:
        return "IND"


# ═══════════════════════════════════════════════════════════════════
#       HELPERS
# ═══════════════════════════════════════════════════════════════════
def clean_name(text):
    if not text:
        return ""
    text = re.sub(r'\[[CBUIcbui]\]', '', text)
    text = re.sub(r'\[[0-9A-Fa-f]{6}\]', '', text)
    text = text.replace('\u3164', ' ').replace('\u00a0', ' ')
    text = ''.join(c for c in text if c.isprintable() or c.isspace())
    return text.strip()


def decode_bio(bio_raw):
    if not bio_raw:
        return ""
    if len(bio_raw) > 20 and all(c in '0123456789abcdefABCDEF' for c in bio_raw):
        try:
            bio_bytes = bytes.fromhex(bio_raw)
            bio_raw = bio_bytes.decode('utf-8', errors='replace')
        except:
            pass
    bio_raw = ''.join(c for c in bio_raw if c.isprintable() or c in '\n\r\t')
    return bio_raw.strip()


def calculate_likes_progress(likes):
    if likes < 100:
        next_milestone = 100
        prev_milestone = 0
    else:
        next_milestone = ((likes // 100) + 1) * 100
        prev_milestone = (likes // 100) * 100

    needed = next_milestone - likes
    total_range = next_milestone - prev_milestone
    current_in_range = likes - prev_milestone
    percentage = round((current_in_range / total_range) * 100, 2) if total_range > 0 else 0

    return {
        "current": likes,
        "next_milestone": next_milestone,
        "needed": needed,
        "progress_percentage": percentage,
        "formatted": f"{likes} / {next_milestone} ({needed} more needed)"
    }


# ═══════════════════════════════════════════════════════════════════
#       OAUTH
# ═══════════════════════════════════════════════════════════════════
async def get_oauth(uid, password):
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/4.0.19P4 (Vivo Y15c; Android 12; en;IN;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": CLIENT_SECRET,
        "client_id": CLIENT_ID
    }
    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        conn = aiohttp.TCPConnector(ssl=ssl_ctx)
        async with aiohttp.ClientSession(connector=conn) as s:
            async with s.post(OAUTH_URL, headers=headers, data=data, timeout=30) as r:
                if r.status != 200:
                    return None, None, f"OAuth HTTP {r.status}"
                j = await r.json()
                oid = j.get("open_id")
                at = j.get("access_token")
                if not oid or not at:
                    return None, None, "Missing oid/token"
                return oid, at, None
    except asyncio.TimeoutError:
        return None, None, "TIMEOUT"
    except Exception as e:
        return None, None, f"{type(e).__name__}"


# ═══════════════════════════════════════════════════════════════════
#       BUILD MAJOR LOGIN
# ═══════════════════════════════════════════════════════════════════
def build_ml(open_id, access_token, region="IND"):
    ml = MajoRLoGinrEq_pb2.MajorLogin()
    ml.event_time = "2026-07-09 12:44:05"
    ml.game_name = "free fire"
    ml.platform_id = 1
    ml.client_version = "1.126.9"
    ml.system_software = "Android OS 13 / API-33"
    ml.system_hardware = "Handheld"
    ml.telecom_operator = "45403"
    ml.network_type = "WIFI"
    ml.screen_width = 1280
    ml.screen_height = 720
    ml.screen_dpi = "320"
    ml.processor_details = "ARM64"
    ml.memory = 128
    ml.gpu_renderer = "Mali-G610"
    ml.gpu_version = "OpenGL ES 3.2"
    ml.unique_device_id = "Google|7a9732a4-2549-4edc-840e-d61263d128f5"
    ml.client_ip = "162.128.224.168"
    ml.language = "en"
    ml.open_id = open_id
    ml.open_id_type = "4"
    ml.device_type = "Handheld"
    ml.device_model = "OPPO CPH2217"
    ml.region = region
    ml.access_token = access_token
    ml.platform_sdk_id = 1
    ml.network_operator_a = "45403"
    ml.network_type_a = "WIFI"
    ml.client_using_version = "1ac4b80ecf0478a44203bf8fac6120f5"
    ml.external_storage_total = 20660
    ml.external_storage_available = 17445
    ml.internal_storage_total = 2663
    ml.internal_storage_available = 1500
    ml.game_disk_storage_available = 17573
    ml.game_disk_storage_total = 20660
    ml.external_sdcard_avail_storage = 17573
    ml.external_sdcard_total_storage = 20660
    ml.login_by = 3
    ml.library_path = "/data/app"
    ml.reg_avatar = 1
    ml.library_token = "4c322aeb56444feaa151d1ea91a8f7f2|apk"
    ml.channel_type = 6
    ml.cpu_type = 2
    ml.cpu_architecture = "64"
    ml.client_version_code = "2019120816"
    ml.unknown_int85 = 3
    ml.graphics_api = "OpenGLES2"
    ml.supported_astc_bitset = 16383
    ml.login_open_id_type = 4
    ml.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    ml.loading_time = 25777
    ml.release_channel = "3rd_party"
    ml.extra_info = "KqsHTz+zAigQ0BOzKhQHN8ae/IefLXcroDjaj4QY+OF71nTuiQh+myDUqCZFPJQ5gyC9LfEeKoon9d461764VIGguRHcIyKfExGAh4bvxFZRgp2X"
    ml.android_engine_init_flag = 110009
    ml.extra_json = '{"cur_rate":null,"support_etc2":false}'
    ml.if_push = 1
    ml.is_vpn = 1
    ml.origin_platform_type = "4"
    ml.primary_platform_type = "4"
    ml.unknown_bytes102 = b"E1JMTwcJXjA2"
    return ml.SerializeToString()


def encrypt_proto(data: bytes) -> bytes:
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(data, AES.block_size))


# ═══════════════════════════════════════════════════════════════════
#       GET JWT
# ═══════════════════════════════════════════════════════════════════
async def get_jwt(oid, at, region="IND"):
    try:
        payload = build_ml(oid, at, region)
        encrypted = encrypt_proto(payload)
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB54"
        }
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        conn = aiohttp.TCPConnector(ssl=ssl_ctx)
        async with aiohttp.ClientSession(connector=conn) as s:
            async with s.post(MAJOR_LOGIN_URL, data=encrypted,
                              headers=headers, timeout=30, ssl=ssl_ctx) as r:
                if r.status != 200:
                    return None, None, f"HTTP {r.status}"
                raw = await r.read()
                res = MajoRLoGinrEs_pb2.MajorLoginRes()
                res.ParseFromString(raw)
                if not res.token:
                    return None, None, "Empty JWT"
                detected = get_region_from_jwt(res.token)
                return res.token, detected or region, None
    except Exception as e:
        return None, None, f"{type(e).__name__}"


# ═══════════════════════════════════════════════════════════════════
#       FETCH PLAYER
# ═══════════════════════════════════════════════════════════════════
async def encode_varint(n):
    out = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)


async def fetch_player_info(jwt, target_uid, region="IND"):
    try:
        uid_bytes = await encode_varint(int(target_uid))
        packet_hex = f"08{uid_bytes.hex()}1007"

        base_url = REGION_URLS.get(region.upper(), REGION_URLS["IND"])
        host = base_url.replace("https://", "")

        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        encrypted = cipher.encrypt(pad(bytes.fromhex(packet_hex), AES.block_size))

        url = f"{base_url}/GetPlayerPersonalShow"
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Authorization': f'Bearer {jwt}',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)',
            'Host': host,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        conn = aiohttp.TCPConnector(ssl=ssl_ctx)
        async with aiohttp.ClientSession(connector=conn) as s:
            async with s.post(url, headers=headers, data=encrypted,
                              timeout=30, ssl=ssl_ctx) as r:
                if r.status != 200:
                    return None
                raw = await r.read()
                if not raw:
                    return None
                data = parse_proto(raw)
                return format_player(data, target_uid)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
#       PROTOBUF PARSER
# ═══════════════════════════════════════════════════════════════════
def read_varint(data, off):
    r = 0; s = 0
    while True:
        b = data[off]
        r |= (b & 0x7F) << s
        off += 1
        if not (b & 0x80): break
        s += 7
    return r, off


def is_valid_text(data: bytes) -> bool:
    try:
        text = data.decode('utf-8')
        if len(text) == 0:
            return False
        printable = sum(1 for c in text if c.isprintable() or c in '\n\r\t')
        ratio = printable / len(text)
        if '\x00' in text.rstrip('\x00'):
            return False
        return ratio >= 0.85
    except UnicodeDecodeError:
        return False


def parse_proto(data):
    result = {}
    off = 0
    while off < len(data):
        try:
            tag, off = read_varint(data, off)
        except:
            break
        field = tag >> 3
        wire = tag & 7

        if wire == 0:
            v, off = read_varint(data, off)
            result[field] = v
        elif wire == 2:
            ln, off = read_varint(data, off)
            if off + ln > len(data):
                break
            v = data[off:off+ln]
            off += ln

            if is_valid_text(v):
                result[field] = v.decode('utf-8')
            else:
                try:
                    nested = parse_proto(v)
                    if nested and len(nested) > 0:
                        result[field] = nested
                    else:
                        result[field] = v.hex()
                except:
                    result[field] = v.hex()
        elif wire == 5:
            result[field] = int.from_bytes(data[off:off+4], 'little')
            off += 4
        elif wire == 1:
            result[field] = int.from_bytes(data[off:off+8], 'little')
            off += 8
        else:
            break
    return result


# ═══════════════════════════════════════════════════════════════════
#       FORMAT PLAYER (MEMBERS FIXED)
# ═══════════════════════════════════════════════════════════════════
def format_player(data, uid):
    result = {
        "status": "success",
        "uid": uid,
        "nickname": "Unknown",
        "level": 0,
        "exp": 0,
        "likes": 0,
        "likes_progress": None,
        "region": "IND",
        "bio": "",
        "avatar_id": 0,
        "banner_id": 0,
        "badge": 0,
        "title_id": 0,
        "bundle_id": 0,
        "created_date": "N/A",
        "last_login": "N/A",
        "account_age_days": 0,
        "account_age_string": "N/A",
        "honor_score": 0,
        "guild": None,
        "powered_by": "ANSH"
    }

    basic = data.get(1, {}) if isinstance(data.get(1), dict) else {}
    if basic:
        result["uid"] = str(basic.get(1, uid))
        nickname = basic.get(3, "Unknown")
        result["nickname"] = clean_name(str(nickname))
        result["level"] = basic.get(6, 0)
        result["exp"] = basic.get(7, 0)
        likes = basic.get(21, 0)
        result["likes"] = likes
        result["region"] = str(basic.get(5, "IND"))

        if likes > 0:
            result["likes_progress"] = calculate_likes_progress(likes)

        for key, field in [("avatar_id", 12), ("banner_id", 14), ("badge", 15),
                           ("title_id", 19), ("bundle_id", 38)]:
            val = basic.get(field, 0)
            if val:
                result[key] = val

        created = basic.get(44)
        if created and isinstance(created, int) and created > 1000000000:
            try:
                dt = datetime.fromtimestamp(created)
                result["created_date"] = dt.strftime("%d %B %Y")
                age_days = (datetime.now() - dt).days
                result["account_age_days"] = age_days

                years = age_days // 365
                months = (age_days % 365) // 30
                days = age_days % 30

                parts = []
                if years > 0:
                    parts.append(f"{years} year{'s' if years != 1 else ''}")
                if months > 0:
                    parts.append(f"{months} month{'s' if months != 1 else ''}")
                if days > 0 and years == 0:
                    parts.append(f"{days} day{'s' if days != 1 else ''}")
                result["account_age_string"] = " ".join(parts) if parts else "New"
            except:
                pass

        last = basic.get(24)
        if last and isinstance(last, int) and last > 1000000000:
            try:
                result["last_login"] = datetime.fromtimestamp(last).strftime("%d %B %Y, %H:%M")
            except:
                pass

    if isinstance(data.get(9), dict):
        bio_raw = data[9].get(9, "")
        result["bio"] = decode_bio(bio_raw)

    # GUILD — members/max SWAPPED (FIXED)
    if isinstance(data.get(6), dict):
        g = data[6]
        # Field 5 = max_members (55)
        # Field 6 = current members (46)
        max_mem = g.get(5, 0)
        cur_mem = g.get(6, 0)

        guild = {
            "id": str(g.get(1, "")),
            "name": clean_name(str(g.get(2, ""))),
            "level": g.get(4, 0),
            "members": cur_mem,           # ✅ current
            "max_members": max_mem        # ✅ max
        }

        if isinstance(data.get(7), dict):
            leader = data[7]
            guild["leader"] = {
                "uid": str(leader.get(1, "")),
                "nickname": clean_name(str(leader.get(3, ""))),
                "level": leader.get(6, 0),
                "exp": leader.get(7, 0),
                "likes": leader.get(21, 0),
                "avatar_id": leader.get(12, 0),
                "banner_id": leader.get(14, 0),
                "badge": leader.get(15, 0),
                "title_id": leader.get(19, 0),
                "bundle_id": leader.get(38, 0),
            }

        result["guild"] = guild

    if isinstance(data.get(11), dict):
        honor = data[11].get(1, 0)
        if honor:
            result["honor_score"] = honor

    return result


# ═══════════════════════════════════════════════════════════════════
#       FLASK APP
# ═══════════════════════════════════════════════════════════════════
app = Flask(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ═══ SERVE WEBSITE ═══
@app.route("/")
def home():
    if os.path.isfile("index.html"):
        return send_from_directory(".", "index.html")
    return json_response({
        "status": "success",
        "api": API_NAME,
        "version": API_VERSION,
        "accounts": len(ACCOUNTS),
        "powered_by": POWERED_BY,
        "endpoints": [
            "/info?uid=<uid>&region=IND",
            "/guild?uid=<uid>&region=IND",
            "/ban?uid=<uid>&region=IND",
            "/health"
        ],
        "regions": list(REGION_URLS.keys())
    })


@app.route("/api")
def api_info():
    return json_response({
        "status": "success",
        "api": API_NAME,
        "version": API_VERSION,
        "accounts": len(ACCOUNTS),
        "powered_by": POWERED_BY,
        "endpoints": [
            "/info?uid=<uid>&region=IND",
            "/guild?uid=<uid>&region=IND",
            "/ban?uid=<uid>&region=IND",
            "/health"
        ],
        "regions": list(REGION_URLS.keys())
    })


@app.route("/health")
def health():
    return json_response({
        "status": "healthy",
        "accounts": len(ACCOUNTS),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ═══ INFO ENDPOINT ═══
@app.route("/info")
def info():
    uid = request.args.get("uid", "").strip()
    region_input = request.args.get("region", "").strip().upper()

    if not uid or not uid.isdigit():
        return json_response({"status": "error", "message": "UID required", "powered_by": POWERED_BY}, 400)
    if not ACCOUNTS:
        return json_response({"status": "error", "message": "No accounts", "powered_by": POWERED_BY}, 503)

    acc = get_next_account()
    oid, at, err = run_async(get_oauth(acc["uid"], acc["password"]))
    if err:
        return json_response({"status": "error", "message": f"OAuth: {err}", "powered_by": POWERED_BY}, 500)

    region = region_input if region_input in REGION_URLS else "IND"
    jwt, detected_region, err = run_async(get_jwt(oid, at, region))
    if err:
        return json_response({"status": "error", "message": f"JWT: {err}", "powered_by": POWERED_BY}, 500)

    if not region_input and detected_region:
        region = detected_region

    result = run_async(fetch_player_info(jwt, uid, region))
    if not result:
        return json_response({"status": "error", "message": "Player not found", "powered_by": POWERED_BY}, 404)

    result["region"] = region
    return json_response(result)


# ═══ GUILD ENDPOINT (FIXED — uses player UID) ═══
@app.route("/guild")
def guild_info():
    uid = request.args.get("uid", "").strip()
    region_input = request.args.get("region", "").strip().upper()

    if not uid or not uid.isdigit():
        return json_response({"status": "error", "message": "Player UID required", "powered_by": POWERED_BY}, 400)
    if not ACCOUNTS:
        return json_response({"status": "error", "message": "No accounts", "powered_by": POWERED_BY}, 503)

    acc = get_next_account()
    oid, at, err = run_async(get_oauth(acc["uid"], acc["password"]))
    if err:
        return json_response({"status": "error", "message": f"OAuth: {err}", "powered_by": POWERED_BY}, 500)

    region = region_input if region_input in REGION_URLS else "IND"
    jwt, detected_region, err = run_async(get_jwt(oid, at, region))
    if err:
        return json_response({"status": "error", "message": f"JWT: {err}", "powered_by": POWERED_BY}, 500)

    if not region_input and detected_region:
        region = detected_region

    result = run_async(fetch_player_info(jwt, uid, region))
    if not result:
        return json_response({"status": "error", "message": "Player not found", "powered_by": POWERED_BY}, 404)

    guild = result.get("guild")
    if not guild or not guild.get("id"):
        return json_response({
            "status": "error",
            "message": "Player is not in any guild",
            "uid": uid,
            "nickname": result.get("nickname"),
            "powered_by": POWERED_BY
        }, 404)

    guild["powered_by"] = POWERED_BY
    return json_response({"status": "success", "guild": guild, "powered_by": POWERED_BY})


# ═══ BAN CHECK ENDPOINT ═══
@app.route("/ban")
def ban_check():
    uid = request.args.get("uid", "").strip()
    region_input = request.args.get("region", "").strip().upper()

    if not uid or not uid.isdigit():
        return json_response({"status": "error", "message": "UID required", "powered_by": POWERED_BY}, 400)
    if not ACCOUNTS:
        return json_response({"status": "error", "message": "No accounts", "powered_by": POWERED_BY}, 503)

    acc = get_next_account()
    oid, at, err = run_async(get_oauth(acc["uid"], acc["password"]))
    if err:
        return json_response({"status": "error", "message": f"OAuth: {err}", "powered_by": POWERED_BY}, 500)

    region = region_input if region_input in REGION_URLS else "IND"
    jwt, detected_region, err = run_async(get_jwt(oid, at, region))
    if err:
        return json_response({"status": "error", "message": f"JWT: {err}", "powered_by": POWERED_BY}, 500)

    if not region_input and detected_region:
        region = detected_region

    result = run_async(fetch_player_info(jwt, uid, region))

    if result and result.get("status") == "success":
        return json_response({
            "status": "success",
            "uid": uid,
            "banned": False,
            "account_status": "ACTIVE",
            "region": region,
            "nickname": result.get("nickname"),
            "level": result.get("level"),
            "likes": result.get("likes"),
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "powered_by": POWERED_BY
        })
    else:
        return json_response({
            "status": "success",
            "uid": uid,
            "banned": True,
            "account_status": "BANNED_OR_DELETED",
            "region": region,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "powered_by": POWERED_BY
        })


# ═══════════════════════════════════════════════════════════════════
#       STARTUP
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("")
    print("╔═══════════════════════════════════════════════╗")
    print("║  🐱 ANSH FF INFO API v12.0 FIXED              ║")
    print("║  Info · Guild · Ban · Vercel Ready            ║")
    print("║  Made with ❤️  by ANSH                        ║")
    print("╚═══════════════════════════════════════════════╝")
    print("")
    load_accounts()
    print(f"🚀 Server starting on http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False)