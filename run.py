from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yaml
import base64
import json
from datetime import datetime
import os

# Konfigurasi Bot Telegram
API_ID = 21635979  # Ganti dengan API ID Telegram
API_HASH = "cbc12884284bc3457360ca9b9d37b94e"
BOT_TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"

app = Client("stb_inject_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Daftar Admin (ID Telegram)
ADMIN_IDS = [6353421952]  # Ganti dengan ID Telegram admin

# 🔘 Menu Utama dengan Banner & Contact Admin
@app.on_message(filters.command(["start", "stb"]))
async def start(client, message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name

    # Tentukan status pengguna
    status = "PREMIUM" if user_id in ADMIN_IDS else "FREE"

    banner = f"""━━━━━━━━━━━━━━━━━━━━━━━
🧿 **BOT PANEL CREATE CONFIG** 🧿
━━━━━━━━━━━━━━━━━━━━━━━
**USER:** {first_name}
**STATUS:** {status}
**CONTACT ADMIN:** @yinnprovpn
━━━━━━━━━━━━━━━━━━━━━━━
🛠 Kirimkan link akun (VMess/VLESS/Trojan) untuk membuat config OpenWRT.
📌 Contoh:
`vmess://...`
━━━━━━━━━━━━━━━━━━━━━━━"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Buat Config STB", callback_data="generate_config")],
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/yinnprovpn")]
    ])

    await message.reply(banner, reply_markup=keyboard, parse_mode="Markdown")

# 📥 Terima Link Akun & Generate Config
@app.on_message(filters.text)
async def generate_stb_config(client, message):
    try:
        akun_link = message.text.strip()

        # Cek format akun
        if akun_link.startswith("vmess://"):
            akun_type = "VMess"
            decoded_data = base64.b64decode(akun_link[8:]).decode("utf-8")
            data = json.loads(decoded_data)
        elif akun_link.startswith("vless://"):
            akun_type = "VLESS"
            data = parse_vless(akun_link)
        elif akun_link.startswith("trojan://"):
            akun_type = "Trojan"
            data = parse_trojan(akun_link)
        else:
            await message.reply("❌ Format akun tidak valid! Kirimkan link yang benar (VMess/VLESS/Trojan).")
            return

        # 🔥 Generate Config .yaml
        stb_config = {
            "proxies": [
                {
                    "name": f"{akun_type}-STB-WS TLS",
                    "type": akun_type.lower(),
                    "server": data["server"],
                    "port": data["port"],
                    "uuid": data.get("id", data.get("uuid", "")),
                    "alterId": data.get("aid", 0),
                    "cipher": "auto" if akun_type.lower() == "vmess" else "none",
                    "udp": True,
                    "tls": data.get("tls", True),
                    "skip-cert-verify": True,
                    "servername": data.get("host", data.get("sni", "")),
                    "network": "ws",
                    "ws-opts": {
                        "path": data.get("path", "/vmess"),
                        "headers": {
                            "Host": data.get("host", data.get("sni", ""))
                        }
                    }
                }
            ]
        }

        yaml_file = f"/tmp/stb_config_{message.from_user.id}.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(stb_config, f, default_flow_style=False)

        # 🔥 Kirim Config ke User
        await message.reply_document(yaml_file, caption="✅ Config STB OpenWRT berhasil dibuat!")
        os.remove(yaml_file)

        # 🔥 Kirim Pesan Sukses
        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pesan_sukses = f"""━━━━━━━━━━━━━━━━━━━━
🧿 **SUCCESS CREATE CONFIG** 🧿
━━━━━━━━━━━━━━━━━━━━
**STATUS:** ✅
**TIPE:** {akun_type}
**TANGGAL:** {tanggal_sekarang}
**CONTACT ADMIN:** @yinnprovpn
━━━━━━━━━━━━━━━━━━━━"""
        await message.reply(pesan_sukses, parse_mode="Markdown")

    except Exception as e:
        await message.reply(f"❌ Error saat membuat config: {e}")

# 🔍 Parsing VLESS
def parse_vless(link):
    parts = link[8:].split("@")
    user_info, server_info = parts[0], parts[1].split("?")[0]
    user_id, host = user_info, server_info.split(":")[0]
    port = server_info.split(":")[1]

    return {
        "server": host,
        "port": port,
        "uuid": user_id,
        "tls": True,
        "sni": host,
        "path": "/",
        "network": "ws"
    }

# 🔍 Parsing Trojan
def parse_trojan(link):
    parts = link[9:].split("@")
    user_info, server_info = parts[0], parts[1].split("?")[0]
    password, host = user_info, server_info.split(":")[0]
    port = server_info.split(":")[1]

    return {
        "server": host,
        "port": port,
        "password": password,
        "tls": True,
        "sni": host,
        "network": "ws"
    }

# Jalankan Bot
if __name__ == "__main__":
    print("Bot Connected ✅")
    app.run()
