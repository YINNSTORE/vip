from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
import requests
import json
import time

# Konfigurasi Bot
TOKEN = "8024500353:AAHg3XnAcWpyow0JdR_3Xz0Z1DGZUE"
ADMIN_IDS = {6353421952}
bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

# Database Sederhana
blocked_users = {}
user_logs = []
TRACK_PHONE = range(1)

def save_log(user_id, username, action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] ID: {user_id} | Username: {username} | Aksi: {action}\n"
    user_logs.append(log_entry)
    with open("logs.txt", "a") as log_file:
        log_file.write(log_entry)

async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    username = user.username if user.username else "(Tidak Ada)"

    if user_id in blocked_users:
        await update.message.reply_text("⛔ Anda telah diblokir.")
        return

    if user_id in ADMIN_IDS:
        await admin_menu(update, context)
        return

    save_log(user_id, username, "User Baru Masuk")
    keyboard = [[InlineKeyboardButton("📍 Track Lokasi dengan Nomor HP", callback_data='track_location')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selamat datang di *Bot Tracking*, klik tombol di bawah untuk tracking lokasi.", parse_mode="Markdown", reply_markup=reply_markup)

async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "track_location":
        await query.message.reply_text("📱 Masukkan nomor HP yang ingin Anda lacak:")
        return TRACK_PHONE
    elif query.data == "logs":
        await logs(update, context)
    elif query.data == "blocked":
        await blocked(update, context)
    elif query.data == "settings":
        await settings(update, context)

async def process_phone(update: Update, context: CallbackContext):
    phone_number = update.message.text
    await update.message.reply_text(f"🔍 Mencari lokasi untuk nomor: {phone_number}...⏳")
    time.sleep(2)
    await update.message.reply_text("✅ Lokasi ditemukan! 🌍\n📍 Koordinat: -6.2088, 106.8456\n🏙️ Kota: Jakarta\n🌎 Negara: Indonesia")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("❌ Tracking dibatalkan.")
    return ConversationHandler.END

async def admin_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📜 Riwayat Pengguna", callback_data='logs')],
        [InlineKeyboardButton("🚫 User Diblokir", callback_data='blocked')],
        [InlineKeyboardButton("⚙️ Pengaturan Bot", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔧 *MENU ADMIN* 🔧", parse_mode="Markdown", reply_markup=reply_markup)

async def logs(update: Update, context: CallbackContext):
    with open("logs.txt", "r") as log_file:
        logs_content = log_file.read()
    await update.message.reply_text(f"📜 *Log Pengguna:*\n{logs_content}"[:4096], parse_mode="Markdown")

async def blocked(update: Update, context: CallbackContext):
    if not blocked_users:
        await update.message.reply_text("✅ Tidak ada user yang diblokir.")
    else:
        message = "🚫 *User yang Diblokir:*\n" + "\n".join([str(uid) for uid in blocked_users.keys()])
        await update.message.reply_text(message, parse_mode="Markdown")

async def settings(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔄 Reset Bot", callback_data='reset_bot')],
        [InlineKeyboardButton("📌 Atur Notifikasi", callback_data='set_notifications')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚙️ *Pengaturan Bot*", parse_mode="Markdown", reply_markup=reply_markup)

async def ban_user(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        banned_id = update.message.reply_to_message.from_user.id
        blocked_users[banned_id] = time.time()
        await update.message.reply_text(f"🚫 User {banned_id} telah diblokir secara permanen.")

async def unblock_user(update: Update, context: CallbackContext):
    user_id = int(update.message.text.split()[-1])
    if user_id in blocked_users:
        del blocked_users[user_id]
        await update.message.reply_text(f"✅ User {user_id} telah di-unblock.")
    else:
        await update.message.reply_text("⚠️ User tidak ditemukan dalam daftar blokir.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("admin", admin_menu))
application.add_handler(CommandHandler("logs", logs))
application.add_handler(CommandHandler("blocked", blocked))
application.add_handler(CommandHandler("settings", settings))
application.add_handler(CommandHandler("ban", ban_user))
application.add_handler(CommandHandler("unban", unblock_user))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(ConversationHandler(
    entry_points=[CallbackQueryHandler(button_callback, pattern='track_location')],
    states={TRACK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_phone)]},
    fallbacks=[CommandHandler("cancel", cancel)]
))

application.run_polling()
