import requests
import json
import time
import schedule
import random
import os
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [6353421952]  # Ganti dengan ID Admin
USER_DB = "users.json"
OTP_HISTORY = "otp_history.json"

OTP_SITES = [
    "https://receive-smss.com/",
    "https://sms24.me/",
    "https://sms-online.co/",
    "https://freephonenum.com/",
    "https://textnow.com/"
]

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

users = load_json(USER_DB)
otp_history = load_json(OTP_HISTORY)

def is_whitelisted(user_id):
    return str(user_id) in users.get("users", {}) and users["users"][str(user_id)].get("approved", False)

bot = Client("otp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private)
def menu(client, message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or "Tidak ada username"

    # Jika user belum terdaftar, tambahkan ke database
    if user_id not in users.get("users", {}):
        users["users"][user_id] = {"username": username, "approved": False, "otp_limit": 0}
        save_json(USER_DB, users)

        # Kirim notifikasi ke admin untuk approve
        for admin_id in ADMIN_IDS:
            bot.send_message(admin_id, 
                f"🔔 *User Baru Masuk!*\n\n👤 *Username:* @{username}\n🆔 *ID:* `{user_id}`\n\n➖➖➖➖➖\n"
                "👉 Pilih aksi:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Terima", callback_data=f"approve_{user_id}")],
                    [InlineKeyboardButton("❌ Tolak", callback_data=f"reject_{user_id}")]
                ])
            ))

    # Jika user belum di-approve, tolak akses
    if not users["users"][user_id]["approved"]:
        message.reply_text("❌ Kamu belum di-approve oleh admin. Tunggu persetujuan!")
        return

    # Tampilkan menu utama
    keyboard_buttons = [
    [InlineKeyboardButton("📲 Dapatkan OTP", callback_data="get_otp")],
    [InlineKeyboardButton("📜 Riwayat OTP", callback_data="history")],
    [InlineKeyboardButton("🔍 Cari Nomor Berdasarkan Negara", callback_data="search_country")],
    [InlineKeyboardButton("🔙 Bantuan", callback_data="help")]
]

if int(user_id) in ADMIN_IDS:
    keyboard_buttons.append([InlineKeyboardButton("🛠️ Panel Admin", callback_data="admin_panel")])

keyboard = InlineKeyboardMarkup(keyboard_buttons)

    if int(user_id) in ADMIN_IDS:
        keyboard.inline_keyboard.append([InlineKeyboardButton("🛠️ Panel Admin", callback_data="admin_panel")])

    message.reply_text("🔹 Pilih menu di bawah:", reply_markup=keyboard)


@bot.on_callback_query(filters.regex("^approve_"))
def approve_user(client, callback_query):
    user_id = callback_query.data.split("_")[1]
    users["users"][user_id]["approved"] = True
    save_json(USER_DB, users)

    bot.send_message(user_id, "✅ Kamu telah disetujui oleh admin! Selamat menggunakan bot.")
    callback_query.message.edit_text(f"✅ User {user_id} telah diterima!")


@bot.on_callback_query(filters.regex("^reject_"))
def reject_user(client, callback_query):
    user_id = callback_query.data.split("_")[1]
    users["users"].pop(user_id, None)
    save_json(USER_DB, users)

    bot.send_message(user_id, "❌ Maaf, permintaan kamu telah ditolak oleh admin.")
    callback_query.message.edit_text(f"❌ User {user_id} telah ditolak.")


@bot.on_callback_query(filters.regex("admin_panel"))
def admin_panel(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Member", callback_data="add_member")],
        [InlineKeyboardButton("📢 Pengumuman", callback_data="send_announcement")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="back")]
    ])
    callback_query.message.edit_text("🛠️ *Panel Admin*", reply_markup=keyboard)


@bot.on_callback_query(filters.regex("add_member"))
def add_member(client, callback_query):
    callback_query.message.edit_text("❗ Kirimkan ID Telegram user yang ingin diapprove.")

    @bot.on_message(filters.private & filters.user(ADMIN_IDS))
    def receive_user_id(client, message):
        user_id = message.text.strip()
        if user_id in users["users"]:
            users["users"][user_id]["approved"] = True
            save_json(USER_DB, users)
            message.reply_text(f"✅ User {user_id} telah ditambahkan!")
        else:
            message.reply_text("❌ User tidak ditemukan!")


@bot.on_callback_query(filters.regex("send_announcement"))
def announcement_menu(client, callback_query):
    callback_query.message.edit_text("❗ Kirim pengumuman yang ingin dikirim ke semua user.")

    @bot.on_message(filters.private & filters.user(ADMIN_IDS))
    def send_announcement(client, message):
        text = message.text or "📢 Pengumuman dari Admin!"
        for user_id in users["users"]:
            try:
                bot.send_message(user_id, text)
            except:
                pass
        message.reply_text("✅ Pengumuman berhasil dikirim ke semua user!")


@bot.on_callback_query(filters.regex("get_otp"))
def get_otp(client, callback_query):
    user_id = str(callback_query.from_user.id)

    if user_id in users and users[user_id].get("otp_limit", 0) >= 3:
        callback_query.message.edit_text("⚠️ Kamu sudah mengambil 3 OTP hari ini. Coba lagi besok!")
        return

    otp_site = random.choice(OTP_SITES)

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(otp_site)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        numbers = soup.find_all("a", class_="numbox")

        if numbers:
            phone_number = numbers[0].text.strip()
            otp_page = numbers[0]["href"]

            callback_query.message.edit_text(f"📞 Nomor Virtual: `{phone_number}`\n🔄 Menunggu OTP...")

            for _ in range(10):
                driver.get(f"{otp_site}{otp_page}")
                time.sleep(5)

                otp_soup = BeautifulSoup(driver.page_source, "html.parser")
                otp_messages = otp_soup.find_all("td", class_="message")

                if otp_messages:
                    otp_code = otp_messages[0].text.strip()
                    driver.quit()
                    callback_query.message.edit_text(f"✅ OTP: `{otp_code}`")
                    return

            driver.quit()
            callback_query.message.edit_text("⚠️ Gagal mengambil OTP. Coba lagi nanti.")
        else:
            driver.quit()
            callback_query.message.edit_text("⚠️ Tidak ada nomor yang tersedia.")
    except:
        callback_query.message.edit_text("⚠️ Error saat mengambil nomor. Coba lagi nanti.")

bot.run()
