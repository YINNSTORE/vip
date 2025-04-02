from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram import InputMediaPhoto, InputMediaVideo
import random
import time
import logging

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

# Setup logging untuk menangkap error
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

# Fungsi untuk menyimpan log
def save_log(user_id, username, action):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] ID: {user_id} | Username: {username} | Aksi: {action}\n"
    user_logs.append(log_entry)
    with open("logs.txt", "a") as log_file:
        log_file.write(log_entry)

# Fungsi untuk mengacak lokasi
def random_location():
    locations = [
        {"city": "Jakarta", "coords": "-6.2088, 106.8456", "country": "Indonesia"},
        {"city": "Bandung", "coords": "-6.9175, 107.6191", "country": "Indonesia"},
        {"city": "Surabaya", "coords": "-7.2504, 112.7688", "country": "Indonesia"},
        {"city": "Yogyakarta", "coords": "-7.7956, 110.3695", "country": "Indonesia"},
        {"city": "Bali", "coords": "-8.3405, 115.0919", "country": "Indonesia"}
    ]
    return random.choice(locations)

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
    keyboard = [
        [InlineKeyboardButton("📍 Track Lokasi dengan Nomor HP", callback_data='track_phone')],
        [InlineKeyboardButton("📍 Track Lokasi dengan Email", callback_data='track_email')],
        [InlineKeyboardButton("📍 Track Lokasi dengan IMEI", callback_data='track_imei')],
        [InlineKeyboardButton("📍 Track Lokasi dengan User-Agent", callback_data='track_useragent')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selamat datang di *Bot Tracking*, klik tombol di bawah untuk tracking lokasi.", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi untuk menangani tombol yang ditekan
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "track_phone":
        query.message.reply_text("📱 Masukkan nomor HP yang ingin Anda lacak:")
        return TRACK_PHONE
    elif query.data == "track_email":
        query.message.reply_text("📧 Masukkan email yang ingin Anda lacak:")
        return TRACK_PHONE  # Menggunakan TRACK_PHONE untuk sementara
    elif query.data == "track_imei":
        query.message.reply_text("🔢 Masukkan IMEI yang ingin Anda lacak:")
        return TRACK_PHONE  # Menggunakan TRACK_PHONE untuk sementara
    elif query.data == "track_useragent":
        query.message.reply_text("🖥️ Masukkan User-Agent yang ingin Anda lacak:")
        return TRACK_PHONE  # Menggunakan TRACK_PHONE untuk sementara
    elif query.data == "logs":
        logs(update, context)
    elif query.data == "blocked":
        blocked(update, context)
    elif query.data == "settings":
        settings(update, context)
    elif query.data == "back":
        return start(update, context)  # Mengembalikan ke menu utama

# Fungsi untuk memproses input lokasi
def process_location_input(update: Update, context: CallbackContext):
    input_data = update.message.text
    # Ambil lokasi acak
    location = random_location()

    update.message.reply_text(f"🔍 Mencari lokasi untuk {input_data}...⏳")
    time.sleep(2)  # Simulasi waktu pemrosesan
    update.message.reply_text(f"✅ Lokasi ditemukan! 🌍\n📍 Koordinat: {location['coords']}\n🏙️ Kota: {location['city']}\n🌎 Negara: {location['country']}")
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
        [InlineKeyboardButton("⚙️ Pengaturan Bot", callback_data='settings')],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back")]
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
        [InlineKeyboardButton("🔔 Atur Notifikasi Lokasi Ditemukan", callback_data='set_notification_location')],
        [InlineKeyboardButton("🔔 Atur Notifikasi Update Bot", callback_data='set_notification_update')],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("⚙️ *Pengaturan Bot*\nPilih pengaturan notifikasi yang ingin Anda atur:", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi untuk mengatur notifikasi
def set_notification_location(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    # Misalnya, kita bisa menambahkan toggle untuk mengaktifkan/menonaktifkan notifikasi lokasi
    query.edit_message_text("✅ Notifikasi lokasi ditemukan sekarang aktif.\n\nKlik tombol kembali untuk kembali ke pengaturan.")
    return settings(update, context)

def set_notification_update(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    # Misalnya, kita bisa menambahkan toggle untuk mengaktifkan/menonaktifkan notifikasi update
    query.edit_message_text("✅ Notifikasi pembaruan bot sekarang aktif.\n\nKlik tombol kembali untuk kembali ke pengaturan.")
    return settings(update, context)

# Fungsi untuk menangani semua error
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

# Menjalankan Bot
def main():
    try:
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CallbackQueryHandler(button_callback))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_location_input))
        dispatcher.add_handler(CommandHandler("cancel", cancel))


# Fungsi untuk mengirim pengumuman
def send_announcement(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_IDS:
        update.message.reply_text("❌ Anda bukan admin!")
        return

    update.message.reply_text("📢 Kirim pengumuman dalam format:\n\n- Teks biasa\n- Gambar\n- Video\n- Stiker")

def handle_announcement(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if str(user_id) not in ADMIN_IDS:
        return

    if update.message.text:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"📢 *PENGUMUMAN:*\n\n{update.message.text}", parse_mode="Markdown")
    elif update.message.photo:
        photo_id = update.message.photo[-1].file_id
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_id, caption="📢 *PENGUMUMAN*", parse_mode="Markdown")
    elif update.message.video:
        video_id = update.message.video.file_id
        context.bot.send_video(chat_id=update.effective_chat.id, video=video_id, caption="📢 *PENGUMUMAN*", parse_mode="Markdown")
    elif update.message.sticker:
        sticker_id = update.message.sticker.file_id
        context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=sticker_id)
    else:
        update.message.reply_text("❌ Format tidak didukung!")

# Menambahkan handler ke dispatcher
dispatcher.add_handler(CommandHandler("pengumuman", send_announcement))
dispatcher.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.video | Filters.sticker, handle_announcement))


        # Handle error
        dispatcher.add_error_handler(error)

        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == '__main__':
    main()
