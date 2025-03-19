import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Konfigurasi Router Totolink
ROUTER_IP = "192.168.0.1"
USERNAME = "admin"  # Ganti sesuai router
PASSWORD = "admin"  # Ganti sesuai router

def login_router():
    """Melakukan autentikasi ke router"""
    url = f"http://{ROUTER_IP}/cgi-bin/luci"
    data = {"username": USERNAME, "password": PASSWORD}
    session = requests.Session()
    response = session.post(url, data=data)

    if response.status_code == 200:
        return session  # Kembalikan session agar bisa digunakan untuk request lain
    else:
        return None

def get_router_status():
    """Mengecek status router"""
    session = login_router()
    if not session:
        return "⚠️ Gagal login ke router."

    url = f"http://{ROUTER_IP}/cgi-bin/luci/admin/status"
    response = session.get(url)

    if response.status_code == 200:
        return "✅ Router dalam kondisi normal."
    else:
        return "⚠️ Gagal mendapatkan status router."

def restart_router(update: Update, context: CallbackContext) -> None:
    """Melakukan restart router"""
    session = login_router()
    if not session:
        update.callback_query.message.reply_text("⚠️ Gagal login ke router.")
        return

    url = f"http://{ROUTER_IP}/cgi-bin/luci/admin/reboot"
    response = session.post(url)

    msg = "✅ Router sedang restart..." if response.status_code == 200 else "⚠️ Gagal restart router."
    update.callback_query.message.reply_text(msg)

def show_status(update: Update, context: CallbackContext) -> None:
    """Menampilkan status router"""
    status = get_router_status()
    update.callback_query.message.reply_text(f"📡 *Status Router:*\n{status}", parse_mode="Markdown")

def menu(update: Update, context: CallbackContext) -> None:
    """Menampilkan menu utama"""
    welcome_message = (
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Selamat Datang di Bot Admin Router Totolink!*\n"
        f"📡 *IP Router:* `{ROUTER_IP}`\n"
        "🔧 *Gunakan tombol di bawah untuk mengontrol router.*\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

    keyboard = [
        [InlineKeyboardButton("📡 Cek Status Router", callback_data="status")],
        [InlineKeyboardButton("🔄 Restart Router", callback_data="restart")],
        [InlineKeyboardButton("🔧 Ubah Admin", callback_data="setadmin")],
        [InlineKeyboardButton("📶 Ubah WiFi", callback_data="setwifi")],
        [InlineKeyboardButton("🚫 Blokir Perangkat", callback_data="block"),
         InlineKeyboardButton("✅ Unblock Perangkat", callback_data="unblock")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

def button_handler(update: Update, context: CallbackContext) -> None:
    """Menangani aksi tombol"""
    query = update.callback_query
    query.answer()

    if query.data == "status":
        show_status(update, context)
    elif query.data == "restart":
        restart_router(update, context)
    elif query.data == "setadmin":
        query.message.reply_text("🔑 Masukkan perintah: `/setadmin username_baru password_baru`")
    elif query.data == "setwifi":
        query.message.reply_text("📶 Masukkan perintah: `/setwifi SSID_baru password_baru`")
    elif query.data == "block":
        query.message.reply_text("🚫 Masukkan perintah: `/block MAC_ADDRESS`")
    elif query.data == "unblock":
        query.message.reply_text("✅ Masukkan perintah: `/unblock MAC_ADDRESS`")

def main():
    TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("menu", menu))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
