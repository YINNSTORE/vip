import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Logging untuk debugging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Token bot
TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"

# ID admin
ADMIN_ID = 6353421952  

# Data user
WHITELIST_USERS = {123456789: "ATMIN", 6353421952: "User2"}  # Format: {user_id: "nama"}
USER_BALANCE = {123456789: 5000, 6353421952: 10000}  # Saldo masing-masing user
user_data = {}

# Fungsi cek akses
async def check_access(update: Update) -> bool:
    user_id = update.message.chat_id
    if user_id not in WHITELIST_USERS:
        await update.message.reply_text("❌ Akses Ditolak! ID Anda tidak terdaftar.")
        return False
    return True

# Menu utama
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_access(update):
        return

    user_id = update.message.chat_id
    status = "ADMIN" if user_id == ADMIN_ID else "MEMBER"
    saldo = USER_BALANCE.get(user_id, 0)

    message = f"""
━━━━━━━━━━━━━━━━━━━━
🧿 BOT PANEL TEMBAK 🧿
━━━━━━━━━━━━━━━━━━━━
STATUS : {status}
SALDO : {saldo}
ID TELE : {user_id}
CONTACTS ADMIN @yinnprovpn
━━━━━━━━━━━━━━━━━━━━
"""
    keyboard = [
        [InlineKeyboardButton("🛒 Beli Paket", callback_data="MENU_BELI_PAKET")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="MENU_CONTACT_ADMIN")],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Setting", callback_data="MENU_SETTING")])

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Beli paket
async def beli_paket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    await query.message.reply_text("📌 Masukkan nomor HP tujuan:")
    user_data[chat_id] = {"step": "waiting_for_number"}

    # Set timeout
    await asyncio.sleep(60)
    if user_data.get(chat_id, {}).get("step") == "waiting_for_number":
        await query.message.reply_text("⏳ **Sesi habis! Operasi dibatalkan.**", parse_mode="Markdown")
        user_data.pop(chat_id, None)

# Pilih paket setelah input nomor HP
async def handle_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    if user_data.get(chat_id, {}).get("step") == "waiting_for_number":
        user_data[chat_id] = {"phone": text, "step": "waiting_for_package"}

        keyboard = [
            [InlineKeyboardButton("📡 Xtra Unlimited Super", callback_data="PAKET_XTRA")],
            [InlineKeyboardButton("🎥 Unlimited Vidio", callback_data="PAKET_VIDIO")],
        ]
        await update.message.reply_text("📦 **Pilih paket:**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Proses beli paket
async def beli_paket_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    paket = query.data

    harga_admin = {"PAKET_XTRA": 2000, "PAKET_VIDIO": 5000}
    harga_member = {"PAKET_XTRA": 5000, "PAKET_VIDIO": 8000}

    user_id = query.message.chat_id
    harga = harga_admin[paket] if user_id == ADMIN_ID else harga_member[paket]

    if USER_BALANCE.get(user_id, 0) < harga:
        await query.message.reply_text("❌ Saldo tidak cukup!")
        return

    USER_BALANCE[user_id] -= harga
    await query.message.reply_text(f"✅ Paket berhasil dibeli! Saldo tersisa: {USER_BALANCE[user_id]}")

# Setting Admin
async def menu_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query.message.chat_id != ADMIN_ID:
        await query.message.reply_text("❌ Akses Ditolak! Hanya admin yang bisa mengakses menu ini.")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Add Member", callback_data="ADD_MEMBER")],
        [InlineKeyboardButton("💰 Add Saldo Member", callback_data="ADD_SALDO")],
        [InlineKeyboardButton("📋 Cek Member", callback_data="CEK_MEMBER")],
    ]
    await query.message.reply_text("⚙️ **Menu Setting** ⚙️\nPilih opsi di bawah:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Add saldo
async def add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.message.reply_text("📌 Masukkan ID Telegram user:")
    user_data[query.message.chat_id] = {"step": "waiting_for_id"}

async def handle_add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    if user_data.get(chat_id, {}).get("step") == "waiting_for_id":
        user_data[chat_id] = {"id": int(text), "step": "waiting_for_amount"}
        await update.message.reply_text("📌 Masukkan jumlah saldo:")
    elif user_data.get(chat_id, {}).get("step") == "waiting_for_amount":
        user_id = user_data[chat_id]["id"]
        amount = int(text)
        USER_BALANCE[user_id] = USER_BALANCE.get(user_id, 0) + amount

        response = f"""
━━━━━━━━━━━━━━━━━━━━
🧿 SUKSES ADD SALDO 🧿
━━━━━━━━━━━━━━━━━━━━
NAMA : {WHITELIST_USERS.get(user_id, 'Unknown')}
ID TELE : {user_id}
SALDO : {amount}
TANGGAL : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
STATUS : ✅ BERHASIL
@yinnprovpn
━━━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(response, parse_mode="Markdown")
        user_data.pop(chat_id, None)

# Cek member
async def cek_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    message = "━━━━━━━━━━━━━━━━━━━━\n🧿 **DAFTAR MEMBER** 🧿\n━━━━━━━━━━━━━━━━━━━━\n"
    for user_id, name in WHITELIST_USERS.items():
        saldo = USER_BALANCE.get(user_id, 0)
        message += f"NAMA : {name}\nID TELE : {user_id}\nSALDO : {saldo}\n━━━━━━━━━━━━━━━━━━━━\n"
    await query.message.reply_text(message, parse_mode="Markdown")

# Jalankan bot
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CommandHandler("timeout", menu))
    app.add_handler(CallbackQueryHandler(beli_paket, pattern="^MENU_BELI_PAKET"))
    app.add_handler(CallbackQueryHandler(menu_setting, pattern="^MENU_SETTING"))
    app.add_handler(CallbackQueryHandler(add_saldo, pattern="^ADD_SALDO"))
    app.add_handler(CallbackQueryHandler(cek_member, pattern="^CEK_MEMBER"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_saldo))
    app.run_polling()

if __name__ == "__main__":
    main()
    