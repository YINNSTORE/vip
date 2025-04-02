import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import random
import string
import time  # Untuk menambah delay

# Bot Token dan ID Admin
API_TOKEN = '8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE'
ADMIN_ID = '6353421952'  # Ganti dengan ID Telegram admin kamu
bot = telebot.TeleBot(API_TOKEN)

# Database untuk tracking user dan trial
user_data = {}

# Fungsi untuk mengirim pesan dengan tombol
def send_welcome(message):
    user_id = message.chat.id
    markup = InlineKeyboardMarkup()

    # Menu Admin
    if is_admin(user_id):
        markup.add(
            InlineKeyboardButton("📂 My APK", callback_data="my_apk"),
            InlineKeyboardButton("🔄 Modifikasi APK", callback_data="modifikasi_apk"),
            InlineKeyboardButton("📖 Panduan", callback_data="panduan"),
            InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")  # Only for admin
        )
        bot.send_message(user_id, "Selamat datang di Bot Modifikasi APK 🔥\nPilih menu admin di bawah:", reply_markup=markup)
    
    # Menu Member
    else:
        markup.add(
            InlineKeyboardButton("🎁 Trial VIP 3 Hari", callback_data="trial_vip"),
            InlineKeyboardButton("📂 My APK", callback_data="my_apk"),
            InlineKeyboardButton("🔄 Modifikasi APK", callback_data="modifikasi_apk"),
            InlineKeyboardButton("📖 Panduan", callback_data="panduan"),
            InlineKeyboardButton("💰 Upgrade ke Premium", callback_data="upgrade_premium")
        )
        bot.send_message(user_id, "Selamat datang di Bot Modifikasi APK 🔥\nPilih menu di bawah untuk mulai.", reply_markup=markup)

# Fungsi untuk mengelola trial
def check_trial(user_id):
    today = datetime.datetime.now()
    if user_id not in user_data:
        user_data[user_id] = {"trial_start": today, "invites": 0}
    trial_start = user_data[user_id]["trial_start"]
    trial_end = trial_start + datetime.timedelta(days=3)

    if today > trial_end:
        return False  # Trial sudah habis
    return True  # Trial masih berlaku

# Fungsi untuk mengundang teman
def generate_referral_link(user_id):
    unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"https://t.me/bangumberacc4bot?start={user_id}_{unique_code}"

# Fungsi untuk mengecek apakah user adalah admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Fungsi Admin Panel
def admin_panel(user_id):
    if is_admin(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔧 Manage User", callback_data="manage_user"),
            InlineKeyboardButton("⚙️ System Settings", callback_data="system_settings")
        )
        bot.send_message(user_id, "Selamat datang di Admin Panel! Pilih menu untuk melanjutkan.", reply_markup=markup)
    else:
        bot.send_message(user_id, "❌ Kamu tidak memiliki akses ke panel admin!")

# Fungsi untuk menangani trial dan referral
@bot.callback_query_handler(func=lambda call: call.data == "trial_vip")
def handle_trial_vip(call):
    user_id = call.message.chat.id
    trial_status = check_trial(user_id)

    if trial_status:
        sent_message = bot.send_message(user_id, "🎉 Kamu sudah mendapatkan Trial VIP 3 Hari!\nNikmati fitur premium yang tersedia!")
        time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
        bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
    else:
        sent_message = bot.send_message(user_id, "❌ Trial VIP 3 Hari kamu sudah habis.\nSilakan undang teman untuk mendapatkan trial baru!")
        # Kirimkan link referral
        referral_link = generate_referral_link(user_id)
        bot.send_message(user_id, f"Undang teman menggunakan link ini untuk mendapatkan trial VIP:\n{referral_link}")
        time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
        bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik

# Fungsi untuk menangani callback dari tombol lain
@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    user_id = call.message.chat.id
    if call.data == "my_apk":
        sent_message = bot.send_message(user_id, "🔄 Untuk melihat APK yang sudah dimodifikasi, upload APK yang diinginkan!")
        time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
        bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
    elif call.data == "modifikasi_apk":
        sent_message = bot.send_message(user_id, "🔄 Silakan upload APK yang ingin dimodifikasi.")
        time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
        bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
    elif call.data == "panduan":
        sent_message = bot.send_message(user_id, "📖 Panduan penggunaan bot:\n1. Pilih 'Trial VIP 3 Hari' untuk memulai.\n2. Undang teman untuk mendapatkan lebih banyak waktu trial.")
        time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
        bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
    elif call.data == "upgrade_premium":
        sent_message = bot.send_message(user_id, "💰 Untuk upgrade ke Premium, kunjungi situs kami atau hubungi Admin!")
        time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
        bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
    elif call.data == "admin_panel":
        admin_panel(user_id)
    elif call.data == "manage_user":
        if is_admin(user_id):
            sent_message = bot.send_message(user_id, "🔧 Fitur Manage User akan segera tersedia!")
            time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
            bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
        else:
            sent_message = bot.send_message(user_id, "❌ Akses ditolak! Hanya admin yang bisa mengakses fitur ini.")
            time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
            bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
    elif call.data == "system_settings":
        if is_admin(user_id):
            sent_message = bot.send_message(user_id, "⚙️ Fitur System Settings akan segera tersedia!")
            time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
            bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik
        else:
            sent_message = bot.send_message(user_id, "❌ Akses ditolak! Hanya admin yang bisa mengakses fitur ini.")
            time.sleep(5)  # Menunggu 5 detik sebelum menghapus pesan
            bot.delete_message(user_id, sent_message.message_id)  # Menghapus pesan setelah 5 detik

# Fungsi untuk melacak siapa yang mengundang siapa
@bot.message_handler(commands=['start'])
def handle_referral(message):
    user_id = message.chat.id
    referrer = None
    
    # Cek apakah ada referral ID pada URL
    if 'start=' in message.text:
        referrer = message.text.split('start=')[-1]

    # Proses jika ada referrer
    if referrer:
        # Menambah jumlah undangan
        if referrer not in user_data:
            user_data[referrer] = {"trial_start": datetime.datetime.now(), "invites": 0}
        user_data[referrer]["invites"] += 1
        # Beri notifikasi ke user yang mengundang
        bot.send_message(referrer, f"🎉 Kamu telah berhasil mengundang teman! Total undangan: {user_data[referrer]['invites']}")

    send_welcome(message)

# Fungsi untuk memulai bot
bot.polling(none_stop=True)
