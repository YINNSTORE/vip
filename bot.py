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

API_ID = os.getenv("21635979")
API_HASH = os.getenv("cbc12884284bc3457360ca9b9d37b94e")
BOT_TOKEN = os.getenv("7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg")

ADMIN_IDS = [6353421952]
USER_DB = "users.json"
OTP_HISTORY = "otp_history.json"

OTP_SITES = [
    "https://receive-smss.com/",
    "https://sms24.me/",
    "https://sms-online.co/",
    "https://freephonenum.com/",
    "https://textnow.com/"
]

PROXY_LIST = ["http://proxy1.com:8080", "http://proxy2.com:8080"]
PROXY_API = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http"

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
    return str(user_id) in users

def get_proxy():
    try:
        response = requests.get(PROXY_API)
        proxy_list = response.text.split("\n")
        return random.choice(proxy_list).strip()
    except:
        return random.choice(PROXY_LIST)

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

bot = Client("otp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private)
def menu(client, message):
    user_id = str(message.from_user.id)

    if not is_whitelisted(user_id):
        message.reply_text("❌ Kamu belum di-approve oleh admin. Tunggu persetujuan!")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 Dapatkan OTP", callback_data="get_otp")],
        [InlineKeyboardButton("📜 Riwayat OTP", callback_data="history")],
        [InlineKeyboardButton("🔍 Cari Nomor Berdasarkan Negara", callback_data="search_country")],
        [InlineKeyboardButton("🔙 Bantuan", callback_data="help")]
    ])

    if int(user_id) in ADMIN_IDS:
        keyboard.inline_keyboard.append([InlineKeyboardButton("🛠️ Panel Admin", callback_data="admin_panel")])

    message.reply_text("🔹 Pilih menu di bawah:", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("get_otp"))
def get_otp(client, callback_query):
    user_id = str(callback_query.from_user.id)

    if user_id in users and users[user_id].get("otp_limit", 0) >= 3:
        callback_query.message.edit_text("⚠️ Kamu sudah mengambil 3 OTP hari ini. Coba lagi besok!")
        return

    otp_site = random.choice(OTP_SITES)
    proxy = get_proxy()

    try:
        driver = setup_selenium()
        driver.get(otp_site)
        time.sleep(5)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        numbers = soup.find_all("a", class_="numbox")

        if numbers:
            phone_number = numbers[0].text.strip()
            otp_page = numbers[0]["href"]

            callback_query.message.edit_text(f"📞 Nomor Virtual: `{phone_number}`\n🔄 Menunggu OTP...")

            for _ in range(10):
                driver.get(f"{otp_site}{otp_page}")
                time.sleep(5)

                page_source = driver.page_source
                otp_soup = BeautifulSoup(page_source, "html.parser")
                otp_messages = otp_soup.find_all("td", class_="message")

                if otp_messages:
                    otp_code = otp_messages[0].text.strip()

                    if user_id in users:
                        users[user_id]["otp_limit"] = users[user_id].get("otp_limit", 0) + 1

                    otp_history[user_id] = otp_history.get(user_id, []) + [otp_code]
                    save_json(USER_DB, users)
                    save_json(OTP_HISTORY, otp_history)

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

@bot.on_callback_query(filters.regex("history"))
def history(client, callback_query):
    user_id = str(callback_query.from_user.id)
    history_list = otp_history.get(user_id, ["Belum ada OTP yang digunakan"])

    text = "\n".join(history_list[-5:])
    callback_query.message.edit_text(f"📜 *Riwayat OTP:*\n{text}")

@bot.on_callback_query(filters.regex("help"))
def help_menu(client, callback_query):
    callback_query.message.edit_text("""
📌 *Cara Menggunakan Bot OTP*
1️⃣ Klik tombol *Dapatkan OTP* untuk menerima nomor virtual.
2️⃣ Tunggu hingga nomor tersedia.
3️⃣ Bot akan otomatis mengambil OTP tanpa harus klik tombol.
4️⃣ Jika ingin melihat riwayat OTP yang pernah digunakan, tekan *Riwayat OTP*.
""")

# **🔴 Fitur Auto-Semat Pesan 🔴**
@bot.on_message(filters.private)
def auto_pin_message(client, message):
    chat_id = message.chat.id

    if message.reply_to_message:
        try:
            client.pin_chat_message(chat_id, message.reply_to_message.id, disable_notification=True)
        except:
            pass  

# **🔴 Fitur Pengumuman Admin 🔴**
@bot.on_message(filters.private & filters.user(ADMIN_IDS))
def send_announcement(client, message):
    """Fitur Pengumuman Admin - Bisa kirim teks, foto, stiker, atau dokumen ke semua user"""
    text = message.text if message.text else "📢 Pengumuman dari Admin!"
    
    for user_id in users.keys():
        try:
            if message.photo:
                client.send_photo(user_id, photo=message.photo.file_id, caption=text)
            elif message.sticker:
                client.send_sticker(user_id, sticker=message.sticker.file_id)
            elif message.document:
                client.send_document(user_id, document=message.document.file_id, caption=text)
            else:
                client.send_message(user_id, text)
        except:
            pass  

    message.reply_text("✅ Pengumuman berhasil dikirim ke semua user!")

def reset_daily_limit():
    for user in users:
        users[user]["otp_limit"] = 0
    save_json(USER_DB, users)

schedule.every().day.at("00:00").do(reset_daily_limit)

bot.run()
