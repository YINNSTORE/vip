from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
import requests
import json
import time

# Konfigurasi Bot
TOKEN = "YOUR_BOT_TOKEN"
ADMIN_IDS = {"YOUR_ADMIN_ID"}  # Bisa lebih dari satu admin
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Database Sederhana untuk User yang Diblokir dan Log
blocked_users = {}
user_attempts = {}
user_logs = []
MAX_ATTEMPTS = 2
AUTO_UNBLOCK_TIME = 3600  # 1 jam
TRACK_PHONE = range(1)

def save_log(user_id, username, action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] ID: {user_id} | Username: {username} | Aksi: {action}\n"
    user_logs.append(log_entry)
    with open("logs.txt", "a") as log_file:
        log_file.write(log_entry)

def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "(Tidak Ada)"
    
    if user_id in blocked_users:
        update.message.reply_text("⛔ Anda telah diblokir dan tidak bisa menggunakan bot ini.")
        return
    
    if str(user_id) in ADMIN_IDS:
        return admin_menu(update, context)
    
    save_log(user_id, username, "User Baru Masuk")
    keyboard = [[InlineKeyboardButton("📍 Track Lokasi dengan Nomor HP", callback_data='track_location')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selamat datang di *Bot Tracking*, klik tombol di bawah untuk tracking lokasi.", parse_mode="Markdown", reply_markup=reply_markup)

def track_location(update: Update, context: CallbackContext):
    update.callback_query.answer()
    update.callback_query.message.reply_text("📱 Masukkan nomor HP yang ingin Anda lacak:")
    return TRACK_PHONE

def process_phone(update: Update, context: CallbackContext):
    phone_number = update.message.text
    update.message.reply_text(f"🔍 Mencari lokasi untuk nomor: {phone_number}...⏳")
    time.sleep(2)  # Simulasi pencarian
    update.message.reply_text("✅ Lokasi ditemukan! 🌍\n📍 Koordinat: -6.2088, 106.8456\n🏙️ Kota: Jakarta\n🌎 Negara: Indonesia")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Tracking dibatalkan.")
    return ConversationHandler.END

def admin_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📜 Riwayat Pengguna", callback_data='logs')],
        [InlineKeyboardButton("🚫 User Diblokir", callback_data='blocked')],
        [InlineKeyboardButton("⚙️ Pengaturan Bot", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🔧 *MENU ADMIN* 🔧", parse_mode="Markdown", reply_markup=reply_markup)

def logs(update: Update, context: CallbackContext):
    with open("logs.txt", "r") as log_file:
        logs_content = log_file.read()
    update.message.reply_text(f"📜 *Log Pengguna:*\n{logs_content}"[:4096], parse_mode="Markdown")

def blocked(update: Update, context: CallbackContext):
    if not blocked_users:
        update.message.reply_text("✅ Tidak ada user yang diblokir.")
    else:
        message = "🚫 *User yang Diblokir:*\n" + "\n".join([str(uid) for uid in blocked_users.keys()])
        update.message.reply_text(message, parse_mode="Markdown")

def settings(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔄 Reset Bot", callback_data='reset_bot')],
        [InlineKeyboardButton("📌 Atur Notifikasi", callback_data='set_notifications')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("⚙️ *Pengaturan Bot*\nAtur pengaturan sesuai kebutuhan.", parse_mode="Markdown", reply_markup=reply_markup)

def ban_user(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        banned_id = update.message.reply_to_message.from_user.id
        blocked_users[banned_id] = time.time()
        update.message.reply_text(f"🚫 User {banned_id} telah diblokir secara permanen.")

def unblock_user(update: Update, context: CallbackContext):
    user_id = update.message.text.split()[-1]
    if user_id in blocked_users:
        del blocked_users[user_id]
        update.message.reply_text(f"✅ User {user_id} telah di-unblock.")
    else:
        update.message.reply_text("⚠️ User tidak ditemukan dalam daftar blokir.")

def delete_old_messages(update: Update, context: CallbackContext):
    context.job_queue.run_repeating(auto_delete_messages, interval=60, first=0)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("admin", admin_menu))
dispatcher.add_handler(CommandHandler("logs", logs))
dispatcher.add_handler(CommandHandler("blocked", blocked))
dispatcher.add_handler(CommandHandler("settings", settings))
dispatcher.add_handler(CommandHandler("ban", ban_user))
dispatcher.add_handler(CommandHandler("unban", unblock_user))

dispatcher.add_handler(ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('📍 Track Lokasi dengan Nomor HP'), track_location)],
    states={TRACK_PHONE: [MessageHandler(Filters.text & ~Filters.command, process_phone)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

updater.start_polling()
updater.idle()
