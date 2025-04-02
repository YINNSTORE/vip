from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import time

# Konfigurasi Bot
TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"
ADMIN_IDS = {"6353421952"}
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

# Database Sederhana
blocked_users = {}
user_logs = []
TRACK_PHONE = range(1)

# Fungsi untuk menyimpan log
def save_log(user_id, username, action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] ID: {user_id} | Username: {username} | Aksi: {action}\n"
    user_logs.append(log_entry)
    with open("logs.txt", "a") as log_file:
        log_file.write(log_entry)

# Fungsi untuk memulai percakapan
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "(Tidak Ada)"

    if user_id in blocked_users:
        update.message.reply_text("⛔ Anda telah diblokir.")
        return

    if str(user_id) in ADMIN_IDS:
        return admin_menu(update, context)

    save_log(user_id, username, "User Baru Masuk")
    keyboard = [[InlineKeyboardButton("📍 Track Lokasi dengan Nomor HP", callback_data='track_location')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selamat datang di *Bot Tracking*, klik tombol di bawah untuk tracking lokasi.", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi untuk menangani tombol yang ditekan
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "track_location":
        query.message.reply_text("📱 Masukkan nomor HP yang ingin Anda lacak:")
        return TRACK_PHONE
    elif query.data == "logs":
        logs(update, context)
    elif query.data == "blocked":
        blocked(update, context)
    elif query.data == "settings":
        settings(update, context)

# Fungsi untuk memproses input nomor telepon
def process_phone(update: Update, context: CallbackContext):
    phone_number = update.message.text
    update.message.reply_text(f"🔍 Mencari lokasi untuk nomor: {phone_number}...⏳")
    time.sleep(2)
    update.message.reply_text("✅ Lokasi ditemukan! 🌍\n📍 Koordinat: -6.2088, 106.8456\n🏙️ Kota: Jakarta\n🌎 Negara: Indonesia")
    return ConversationHandler.END

# Fungsi untuk membatalkan percakapan
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Tracking dibatalkan.")
    return ConversationHandler.END

# Menu Admin
def admin_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📜 Riwayat Pengguna", callback_data='logs')],
        [InlineKeyboardButton("🚫 User Diblokir", callback_data='blocked')],
        [InlineKeyboardButton("⚙️ Pengaturan Bot", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🔧 *MENU ADMIN* 🔧", parse_mode="Markdown", reply_markup=reply_markup)

# Menampilkan log pengguna
def logs(update: Update, context: CallbackContext):
    with open("logs.txt", "r") as log_file:
        logs_content = log_file.read()
    update.message.reply_text(f"📜 *Log Pengguna:*\n{logs_content}"[:4096], parse_mode="Markdown")

# Menampilkan user yang diblokir
def blocked(update: Update, context: CallbackContext):
    if not blocked_users:
        update.message.reply_text("✅ Tidak ada user yang diblokir.")
    else:
        message = "🚫 *User yang Diblokir:*\n" + "\n".join([str(uid) for uid in blocked_users.keys()])
        update.message.reply_text(message, parse_mode="Markdown")

# Pengaturan Bot
def settings(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔄 Reset Bot", callback_data='reset_bot')],
        [InlineKeyboardButton("📌 Atur Notifikasi", callback_data='set_notifications')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("⚙️ *Pengaturan Bot*", parse_mode="Markdown", reply_markup=
    