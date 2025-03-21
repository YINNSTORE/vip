import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yaml
import os
import base64
import json
import time
import psutil
from datetime import datetime

# Token bot Telegram
TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"
bot = telebot.TeleBot(TOKEN)

# ID Admin
ADMIN_ID = 6353421952  # Ganti dengan ID admin yang sesuai

# Catat waktu bot mulai berjalan
start_time = time.time()

# Variabel untuk menyimpan sementara input pengguna
user_data = {}

# Menyimpan riwayat akses
access_history = []

# Parsing link akun
def parse_account(link):
    if link.startswith("vmess://"):
        try:
            decoded = base64.b64decode(link.split("vmess://")[1] + "==").decode("utf-8")
            vmess_data = json.loads(decoded)
            port = "443" if vmess_data.get("tls", "").lower() == "tls" else "80"
            name = vmess_data.get("ps", "NoName")
            return {
                "type": "vmess",
                "server": vmess_data["add"],
                "port": port,
                "uuid": vmess_data["id"],
                "path": vmess_data.get("path", "/"),
                "servername": vmess_data["add"],
                "name": name,
            }
        except Exception:
            return None

    elif link.startswith("vless://"):
        try:
            parts = link.split("@")
            uuid = parts[0].split("vless://")[1]
            server_info = parts[1].split(":")
            server = server_info[0]
            port = server_info[1].split("?")[0]
            return {
                "type": "vless",
                "server": server,
                "port": port,
                "uuid": uuid,
                "path": "/",
                "servername": server,
                "name": uuid,
            }
        except Exception:
            return None

    elif link.startswith("trojan://"):
        try:
            parts = link.split("@")
            password = parts[0].split("trojan://")[1]
            server_info = parts[1].split(":")
            server = server_info[0]
            port = server_info[1].split("?")[0]
            return {
                "type": "trojan",
                "server": server,
                "port": port,
                "uuid": password,
                "path": "/",
                "servername": server,
                "name": password,
            }
        except Exception:
            return None

    return None

# Fungsi buat config OpenClash
def generate_openclash_config(user_id):
    data = user_data.get(user_id, {})
    parsed_data = parse_account(data.get("link_akun"))

    if not parsed_data:
        return None  # Jika link tidak valid, return None

    config = {
        "proxies": [
            {
                "name": parsed_data["name"],
                "server": data.get("bug", parsed_data["server"]),
                "port": int(parsed_data["port"]),
                "type": parsed_data["type"],
                "uuid": parsed_data["uuid"],
                "alterId": 0 if parsed_data["type"] == "vmess" else None,
                "cipher": "auto" if parsed_data["type"] == "vmess" else None,
                "tls": False,
                "skip-cert-verify": True,
                "servername": parsed_data["servername"],
                "network": "ws",
                "ws-opts": {
                    "path": parsed_data["path"],
                    "headers": {"Host": parsed_data["servername"]}
                },
                "udp": True
            }
        ]
    }

    filename = f"{data.get('custom_name', 'OpenClash')}.yaml"

    with open(filename, "w") as file:
        yaml.dump(config, file, default_flow_style=False)

    return filename

# Menu utama
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🧿 𝗜𝗡𝗣𝗨𝗧 𝗟𝗜𝗡𝗞 𝗔𝗞𝗨𝗡", callback_data="input_link"),
        InlineKeyboardButton("🧿 𝗜𝗦𝗜 𝗕𝗨𝗚 (𝗢𝗣𝗦𝗜𝗢𝗡𝗔𝗟)", callback_data="input_bug"),
        InlineKeyboardButton("🧿 𝗖𝗨𝗦𝗧𝗢𝗠 𝗡𝗔𝗠𝗔 𝗖𝗢𝗡𝗙𝗜𝗚", callback_data="custom_nama"),
        InlineKeyboardButton("🧿 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗖𝗢𝗡𝗙𝗜𝗚", callback_data="generate_config"),
        InlineKeyboardButton("🖥️ 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 𝗕𝗢𝗧", callback_data="running_bot")
    )

    # Jika pengakses adalah admin, tambahkan tombol Riwayat Akses dan Pengumuman
    if message.chat.id == ADMIN_ID:
        markup.add(
            InlineKeyboardButton("🖥️ 𝗥𝗜𝗪𝗔𝗬𝗔𝗧 𝗔𝗞𝗦𝗘𝗦", callback_data="access_history"),
            InlineKeyboardButton("📢 𝗣𝗘𝗡𝗚𝗨𝗠𝗨𝗠𝗔𝗡", callback_data="send_announcement")
        )

    bot.send_message(message.chat.id, "🚩 Selamat datang di bot auto konfigurasi OpenClash STB OpenWRT By 👤@yinnprovpn", reply_markup=markup)

# Handler tombol menu
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id

    if call.data == "running_bot":
        bot.send_message(user_id, get_bot_status(), parse_mode="Markdown")
    elif call.data == "input_link":
        bot.send_message(user_id, "Silakan kirimkan link akun VMess/VLESS/Trojan Anda:")
        bot.register_next_step_handler(call.message, receive_link)
    elif call.data == "input_bug":
        bot.send_message(user_id, "Silakan kirimkan bug (opsional, jika tidak ada ketik '-').")
        bot.register_next_step_handler(call.message, receive_bug)
    elif call.data == "custom_nama":
        bot.send_message(user_id, "Silakan masukkan nama custom untuk file config:")
        bot.register_next_step_handler(call.message, receive_custom_name)
    elif call.data == "generate_config":
        filename = generate_openclash_config(user_id)
        if filename:
            with open(filename, "rb") as file:
                bot.send_document(user_id, file)
            os.remove(filename)
        else:
            bot.send_message(user_id, "Gagal membuat config. Pastikan semua data sudah diinput dengan benar.")
    elif call.data == "access_history" and user_id == ADMIN_ID:
        if access_history:
            history_text = "⚠️ Riwayat Akses Pengguna ⚠️\n"
            history_text += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for entry in access_history:
                history_text += (
                    f"🧑‍💻 ID Pengguna : `{entry['id']}`\n"
                    f"👤 Username : {entry['username']}\n"
                    f"📅 Tanggal Akses : {entry['date']}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                )
            bot.send_message(user_id, history_text)
        else:
            bot.send_message(user_id, "📉 **Belum ada akses yang tercatat.**")
    elif call.data == "send_announcement" and user_id == ADMIN_ID:
        bot.send_message(user_id, "📢 Kirim Pengumuman :")
        bot.register_next_step_handler(call.message, receive_announcement)

# Fungsi menerima pengumuman dari admin
def receive_announcement(message):
    announcement = message.text
    if announcement:
        for entry in access_history:
            user_id = entry["id"]
            try:
                bot.send_message(user_id, f"📢 Pengumuman: {announcement}")
            except Exception as e:
                print(f"Gagal mengirim pesan ke {user_id}: {e}")
        bot.send_message(message.chat.id, "✅ Pengumuman berhasil dikirim ke semua pengguna")
    else:
        bot.send_message(message.chat.id, "❌ Pengumuman kosong. Tidak ada pesan yang dikirim.")

# Fungsi menerima input link akun
def receive_link(message):
    user_id = message.chat.id
    user_data[user_id] = user_data.get(user_id, {})
    user_data[user_id]["link_akun"] = message.text
    # Menyimpan riwayat akses
    access_history.append({
        "id": user_id,
        "username": message.chat.username,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    bot.send_message(user_id, "✅ Link akun berhasil disimpan!")

# Fungsi menerima input bug
def receive_bug(message):
    user_id = message.chat.id
    user_data[user_id] = user_data.get(user_id, {})
    user_data[user_id]["bug"] = None if message.text == "-" else message.text
    bot.send_message(user_id, "✅ Bug berhasil disimpan!")

# Fungsi menerima input custom nama config
def receive_custom_name(message):
    user_id = message.chat.id
    user_data[user_id] = user_data.get(user_id, {})
    user_data[user_id]["custom_name"] = message.text
    bot.send_message(user_id, f"✅ Nama config disimpan: {message.text}")

# Fungsi untuk menampilkan status bot
def get_bot_status():
    uptime = time.time() - start_time
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))

    ram_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    disk_usage = psutil.disk_usage("/").percent

    status_text = (
        "📊 **SYSTEM STATUS**\n"
        f"🕒 Uptime: `{uptime_str}`\n"
        f"💾 RAM Usage: `{ram_usage}%`\n"
        f"⚙️ CPU Usage: `{cpu_usage}%`\n"
        f"📀 Storage Usage: `{disk_usage}%`\n"
    )
    return status_text

# Menjalankan bot
print("✅ Bot Success Connected.....")
bot.polling()
