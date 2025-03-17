import os
import yaml
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ganti dengan kredensial bot kamu
API_ID = "21635979"
API_HASH = "cbc12884284bc3457360ca9b9d37b94e"
BOT_TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"

bot = Client("clash_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Fungsi untuk decode VMess
def decode_vmess(vmess_link):
    try:
        encoded_data = vmess_link.replace("vmess://", "")
        decoded_data = base64.b64decode(encoded_data + "=" * (-len(encoded_data) % 4)).decode("utf-8")
        return yaml.safe_load(decoded_data)
    except:
        return None

# Fungsi buat file YAML Clash
def generate_yaml(config_data, file_name, protocol):
    config = {
        "proxies": [
            {
                "name": config_data.get("ps", "MyProxy"),
                "type": protocol,
                "server": config_data.get("add"),
                "port": config_data.get("port"),
                "uuid": config_data.get("id") if protocol == "vmess" else None,
                "alterId": config_data.get("aid") if protocol == "vmess" else None,
                "password": config_data.get("id") if protocol == "trojan" else None,
                "cipher": "auto",
                "tls": config_data.get("tls", "false") == "true"
            }
        ]
    }
    
    yaml_path = f"./yinn-clash-{protocol}.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    return yaml_path

# Handle /start dengan button
@bot.on_message(filters.command("start"))
def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 BUAT CONFIG", callback_data="buat_config")]
    ])
    message.reply_text("🔹 Selamat datang di *Yinn Clash Bot*! Klik tombol di bawah untuk buat config.", reply_markup=keyboard)

# Handle tombol "BUAT CONFIG"
@bot.on_callback_query(filters.regex("buat_config"))
def buat_config(client, callback_query):
    callback_query.message.reply_text("⚡ Kirim akun dengan format berikut:\n\n- `vmess://...`\n- `vless://...`\n- `trojan://...`", parse_mode="Markdown")

# Handle link VMess/VLESS/Trojan
@bot.on_message(filters.text & filters.private)
def handle_account(client, message):
    text = message.text.strip()
    
    if text.startswith("vmess://"):
        config_data = decode_vmess(text)
        protocol = "vmess"
    elif text.startswith("vless://"):
        config_data = {"add": text.split("@")[1].split(":")[0], "port": text.split("@")[1].split(":")[1].split("?")[0]}
        protocol = "vless"
    elif text.startswith("trojan://"):
        config_data = {"add": text.split("@")[1].split(":")[0], "port": text.split("@")[1].split(":")[1].split("?")[0], "id": text.split("://")[1].split("@")[0]}
        protocol = "trojan"
    else:
        message.reply_text("❌ Format akun tidak valid!")
        return

    if config_data:
        yaml_path = generate_yaml(config_data, f"yinn-clash-{protocol}", protocol)

        client.send_document(
            chat_id=message.chat.id,
            document=yaml_path,
            caption=f"✅ Konfigurasi Clash berhasil dibuat oleh *Yinn Bot*"
        )

        os.remove(yaml_path)
    else:
        message.reply_text("❌ Gagal membaca akun! Pastikan format benar.")

bot.run()
