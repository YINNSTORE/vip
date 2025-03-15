import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging untuk debugging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Ganti dengan token bot dari @BotFather
TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"

# ID Telegram admin (ganti dengan ID admin)
ADMIN_ID = 6353421952  

# Daftar ID user yang diperbolehkan mengakses bot (WHITELIST)
WHITELIST_USERS = {123456789: "ATMIN", 6353421952: "User2"}  # Format: {user_id: "nama"}

# Data sementara untuk input admin & nomor HP
user_data = {}

# Fungsi untuk mengecek akses user
async def check_access(update: Update) -> bool:
    user_id = update.message.chat_id
    if user_id not in WHITELIST_USERS:
        await update.message.reply_text("❌ Akses Ditolak! ID Anda tidak terdaftar.")
        return False
    return True

# Fungsi menu utama
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_access(update):
        return

    keyboard = [
        [InlineKeyboardButton("🛒 Beli Paket", callback_data="MENU_BELI_PAKET")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="MENU_CONTACT_ADMIN")],
    ]

    # Jika user adalah admin, tambahkan tombol Setting
    if update.message.chat_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Setting", callback_data="MENU_SETTING")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔵 **Menu Utama** 🔵\nSilakan pilih menu:", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi menu beli paket (memasukkan nomor HP)
async def beli_paket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    await query.message.reply_text("📲 **Masukkan nomor HP tujuan:**", parse_mode="Markdown")
    
    # Simpan status bahwa user sedang input nomor HP
    user_data[chat_id] = {"step": "waiting_for_phone"}

# Fungsi menangani input nomor HP
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id in user_data and user_data[chat_id].get("step") == "waiting_for_phone":
        user_data[chat_id]["phone"] = text
        user_data[chat_id]["step"] = "choosing_package"

        keyboard = [
            [InlineKeyboardButton("📡 Xtra Unlimited Super", callback_data="PAKET_XTRA")],
            [InlineKeyboardButton("🎥 Unlimited Vidio", callback_data="PAKET_VIDIO")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📦 **Pilih paket yang ingin dibeli:**", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi menangani pemilihan paket
async def pilih_paket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    paket = query.data

    if chat_id not in user_data or user_data[chat_id].get("step") != "choosing_package":
        return
    
    user_data[chat_id]["package"] = paket

    # Cek harga berdasarkan role (admin/member)
    if chat_id == ADMIN_ID:
        harga_xtra = "Rp 2.000"
        harga_vidio = "Rp 5.000"
    else:
        harga_xtra = "Rp 5.000"
        harga_vidio = "Rp 8.000"

    if paket == "PAKET_XTRA":
        harga = harga_xtra
        nama_paket = "Xtra Unlimited Super"
    else:
        harga = harga_vidio
        nama_paket = "Unlimited Vidio"

    await query.message.reply_text(f"✅ Paket **{nama_paket}** dipilih.\n💰 Harga: {harga}\n\n🔽 Pilih metode pembayaran:", parse_mode="Markdown")

    # Tampilkan metode pembayaran
    keyboard = [
        [InlineKeyboardButton("💳 GOPAY", callback_data="PAY_GOPAY")],
        [InlineKeyboardButton("💰 DANA", callback_data="PAY_DANA")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("🔽 **Pilih metode pembayaran:**", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi menangani pembayaran
async def pembayaran(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    metode = query.data

    if chat_id not in user_data or "package" not in user_data[chat_id]:
        return

    if metode == "PAY_GOPAY":
        metode_pembayaran = "GOPAY"
        link_pembayaran = "https://gopay.link/pembayaran"
    else:
        metode_pembayaran = "DANA"
        link_pembayaran = "https://dana.id/pembayaran"

    nomor_hp = user_data[chat_id]["phone"]
    paket = user_data[chat_id]["package"]

    # Cek harga berdasarkan role (admin/member)
    if chat_id == ADMIN_ID:
        harga = "Rp 2.000" if paket == "PAKET_XTRA" else "Rp 5.000"
    else:
        harga = "Rp 5.000" if paket == "PAKET_XTRA" else "Rp 8.000"

    await query.message.reply_text(
        f"💰 **Pembayaran via {metode_pembayaran}**\n"
        f"📦 Paket: {('Xtra Unlimited Super' if paket == 'PAKET_XTRA' else 'Unlimited Vidio')}\n"
        f"📲 Nomor: {nomor_hp}\n"
        f"💵 Harga: {harga}\n\n"
        f"🔗 **Silakan bayar melalui link berikut:**\n{link_pembayaran}",
        parse_mode="Markdown"
    )

# Menangani callback query
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "MENU_BELI_PAKET":
        await beli_paket(update, context)
    elif data == "MENU_CONTACT_ADMIN":
        await query.message.reply_text(f"📞 **Hubungi Admin:** [Klik di sini](tg://user?id={ADMIN_ID})", parse_mode="Markdown")
    elif data.startswith("PAKET_"):
        await pilih_paket(update, context)
    elif data.startswith("PAY_"):
        await pembayaran(update, context)

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

    print("✅ Bot berjalan dengan sukses!")
    app.run_polling()

if __name__ == "__main__":
    main()
