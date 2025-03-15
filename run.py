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

# Data sementara untuk input admin
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

# Fungsi menu Setting (khusus admin)
async def menu_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    if chat_id != ADMIN_ID:
        await query.message.reply_text("❌ Akses Ditolak! Hanya admin yang bisa mengakses menu ini.")
        return

    keyboard = [[InlineKeyboardButton("➕ Add Member", callback_data="ADD_MEMBER")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("⚙️ **Menu Setting** ⚙️\nPilih opsi di bawah:", parse_mode="Markdown", reply_markup=reply_markup)

# Fungsi untuk menambahkan user ke whitelist
async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    if chat_id != ADMIN_ID:
        await query.message.reply_text("❌ Akses Ditolak! Hanya admin yang bisa menambah member.")
        return

    await query.message.reply_text("✏️ **Masukkan ID member:**", parse_mode="Markdown")

    # Simpan status bahwa admin sedang input ID
    user_data[chat_id] = {"step": "waiting_for_id"}

# Fungsi menangani input dari admin
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    if chat_id == ADMIN_ID:
        step = user_data.get(chat_id, {}).get("step")

        if step == "waiting_for_id":
            try:
                new_user_id = int(text)
                if new_user_id in WHITELIST_USERS:
                    await update.message.reply_text(f"⚠️ User dengan ID `{new_user_id}` sudah ada di whitelist.", parse_mode="Markdown")
                    return
                
                # Simpan ID sementara dan minta nama
                user_data[chat_id]["new_user_id"] = new_user_id
                user_data[chat_id]["step"] = "waiting_for_name"
                await update.message.reply_text("📝 **Masukkan Nama Member:**", parse_mode="Markdown")

            except ValueError:
                await update.message.reply_text("❌ Format ID tidak valid! Masukkan angka saja.")

        elif step == "waiting_for_name":
            new_user_id = user_data[chat_id].get("new_user_id")

            if new_user_id:
                WHITELIST_USERS[new_user_id] = text

                tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                response = f"""
━━━━━━━━━━━━━━━━━━━━
🧿 SUKSES ADD MEMBER 🧿
━━━━━━━━━━━━━━━━━━━━
NAMA : {text}
ID TELE : {new_user_id}
TANGGAL : {tanggal}
STATUS : ✅ BERHASIL
@yinnprovpn
━━━━━━━━━━━━━━━━━━━━
"""
                await update.message.reply_text(response, parse_mode="Markdown")

                # Hapus status input
                user_data.pop(chat_id, None)

# Menangani callback query
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data == "MENU_BELI_PAKET":
        await query.message.reply_text("Masukkan nomor HP tujuan:")
    elif data == "MENU_CONTACT_ADMIN":
        await query.message.reply_text(f"📞 **Hubungi Admin:** [Klik di sini](tg://user?id={ADMIN_ID})", parse_mode="Markdown")
    elif data == "MENU_SETTING":
        await menu_setting(update, context)
    elif data == "ADD_MEMBER":
        await add_member(update, context)

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^MENU_"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^ADD_MEMBER"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_input))

    print("✅ Bot berjalan dengan sukses!")
    app.run_polling()

if __name__ == "__main__":
    main()
