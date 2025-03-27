import os
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [6353421952]
USER_DB = "users.json"

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

bot = Client("otp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private)
def menu(client, message):
    user_id = str(message.from_user.id)

    if user_id not in users.get("users", {}):
        users["users"][user_id] = {"approved": False}
        save_json(USER_DB, users)

        # Notifikasi ke Admin
        for admin_id in ADMIN_IDS:
            client.send_message(admin_id, f"🔔 *User Baru Masuk!*\n👤 @{message.from_user.username}\n🆔 ID: `{user_id}`", parse_mode="markdown")

    if not users["users"][user_id]["approved"]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Terima", callback_data=f"approve_{user_id}"), InlineKeyboardButton("❌ Tolak", callback_data=f"reject_{user_id}")]
        ])
        message.reply_text("❌ Kamu belum di-approve oleh admin.", reply_markup=keyboard)
        return

    keyboard_buttons = [
        [InlineKeyboardButton("📲 Get OTP", callback_data="get_otp")],
        [InlineKeyboardButton("📜 Riwayat OTP", callback_data="history")],
        [InlineKeyboardButton("🔙 Bantuan", callback_data="help")]
    ]

    if int(user_id) in ADMIN_IDS:
        keyboard_buttons.append([InlineKeyboardButton("🛠️ Panel Admin", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    message.reply_text("🔹 Pilih menu di bawah:", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("^admin_panel$"))
def admin_panel(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Member", callback_data="add_member")],
        [InlineKeyboardButton("📢 Pengumuman", callback_data="announcement")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu")]
    ])
    callback_query.message.edit_text("🛠️ *Admin Panel*", reply_markup=keyboard, parse_mode="markdown")

@bot.on_callback_query(filters.regex("^approve_"))
def approve_user(client, callback_query):
    user_id = callback_query.data.split("_")[1]
    users["users"][user_id]["approved"] = True
    save_json(USER_DB, users)

    client.send_message(user_id, "✅ *Selamat! Kamu sudah di-approve oleh admin.*", parse_mode="markdown")
    callback_query.message.edit_text(f"✅ User `{user_id}` berhasil di-approve!", parse_mode="markdown")

@bot.on_callback_query(filters.regex("^reject_"))
def reject_user(client, callback_query):
    user_id = callback_query.data.split("_")[1]
    users["users"].pop(user_id, None)
    save_json(USER_DB, users)

    client.send_message(user_id, "❌ *Maaf, permintaanmu ditolak.*", parse_mode="markdown")
    callback_query.message.edit_text(f"❌ User `{user_id}` telah ditolak!", parse_mode="markdown")

@bot.on_callback_query(filters.regex("^add_member$"))
def add_member(client, callback_query):
    callback_query.message.edit_text("ℹ️ Kirim ID Telegram user yang ingin ditambahkan.")
    users["waiting_for_id"] = True
    save_json(USER_DB, users)

@bot.on_message(filters.private & filters.text)
def handle_admin_input(client, message):
    if users.get("waiting_for_id"):
        user_id = message.text.strip()
        users["users"][user_id] = {"approved": True}
        save_json(USER_DB, users)

        message.reply_text(f"✅ User `{user_id}` telah ditambahkan!")
        users.pop("waiting_for_id", None)
        save_json(USER_DB, users)

@bot.on_callback_query(filters.regex("^announcement$"))
def send_announcement(client, callback_query):
    callback_query.message.edit_text("ℹ️ Kirim pengumuman yang ingin dikirim ke semua user.")
    users["waiting_for_announcement"] = True
    save_json(USER_DB, users)

@bot.on_message(filters.private & filters.text)
def handle_announcement(client, message):
    if users.get("waiting_for_announcement"):
        text = message.text
        for user_id in users["users"].keys():
            client.send_message(user_id, f"📢 *Pengumuman:*\n{text}", parse_mode="markdown")

        message.reply_text("✅ Pengumuman berhasil dikirim!")
        users.pop("waiting_for_announcement", None)
        save_json(USER_DB, users)

bot.run()
