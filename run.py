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
WHITELIST_USERS = {123456789: "Aing", 6353421952: "User2"}  
USER_BALANCE = {123456789: 5000, 6353421952: 10000}  
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
CONTACT ADMIN [@yinnprovpn](https://t.me/yinnprovpn)
━━━━━━━━━━━━━━━━━━━━
"""
    keyboard = [
        [InlineKeyboardButton("🛒 Beli Paket", callback_data="MENU_BELI_PAKET")],
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/yinnprovpn")],
    ]
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Setting", callback_data="MENU_SETTING")])

    await update.message.reply_text(message, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# Menu Setting (Admin Only)
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

# Add Member (Format List Sukses)
async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.message.reply_text("📌 **Masukkan ID Telegram member:**", parse_mode="Markdown")
    user_data[query.message.chat_id] = {"step": "waiting_for_id"}

async def handle_add_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    if user_data.get(chat_id, {}).get("step") == "waiting_for_id":
        try:
            new_user_id = int(text)
            if new_user_id in WHITELIST_USERS:
                await update.message.reply_text(f"⚠️ User dengan ID `{new_user_id}` sudah ada di whitelist.", parse_mode="Markdown")
                return

            user_data[chat_id] = {"new_user_id": new_user_id, "step": "waiting_for_name"}
            await update.message.reply_text("📌 **Masukkan Nama Member:**", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Format ID tidak valid! Masukkan angka saja.")

    elif user_data.get(chat_id, {}).get("step") == "waiting_for_name":
        new_user_id = user_data[chat_id]["new_user_id"]

        WHITELIST_USERS[new_user_id] = text
        USER_BALANCE[new_user_id] = 50000  

        response = f"""
━━━━━━━━━━━━━━━━━━━━
🧿 SUKSES ADD MEMBER 🧿
━━━━━━━━━━━━━━━━━━━━
NAMA : {text}
ID TELE : {new_user_id}
SALDO AWAL : 50.000
TANGGAL : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
STATUS : ✅ BERHASIL
@yinnprovpn
━━━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(response, parse_mode="Markdown")
        user_data.pop(chat_id, None)

# Add Saldo (Format List Sukses)
async def add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.message.reply_text("📌 **Masukkan ID Telegram user:**", parse_mode="Markdown")
    user_data[query.message.chat_id] = {"step": "waiting_for_id_saldo"}

async def handle_add_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    if user_data.get(chat_id, {}).get("step") == "waiting_for_id_saldo":
        try:
            target_id = int(text)
            if target_id not in WHITELIST_USERS:
                await update.message.reply_text("❌ User tidak ditemukan di whitelist.")
                return

            user_data[chat_id] = {"target_id": target_id, "step": "waiting_for_saldo"}
            await update.message.reply_text("📌 **Masukkan jumlah saldo yang ingin ditambahkan:**", parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("❌ Format ID tidak valid! Masukkan angka saja.")

    elif user_data.get(chat_id, {}).get("step") == "waiting_for_saldo":
        try:
            amount = int(text)
            target_id = user_data[chat_id]["target_id"]

            USER_BALANCE[target_id] += amount

            response = f"""
━━━━━━━━━━━━━━━━━━━━
🧿 SUKSES ADD SALDO 🧿
━━━━━━━━━━━━━━━━━━━━
NAMA : {WHITELIST_USERS.get(target_id, 'Unknown')}
ID TELE : {target_id}
SALDO DITAMBAHKAN : {amount}
SALDO TOTAL : {USER_BALANCE[target_id]}
TANGGAL : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
STATUS : ✅ BERHASIL
@yinnprovpn
━━━━━━━━━━━━━━━━━━━━
"""
            await update.message.reply_text(response, parse_mode="Markdown")
            user_data.pop(chat_id, None)
        except ValueError:
            await update.message.reply_text("❌ Format saldo tidak valid! Masukkan angka saja.")

# Jalankan bot
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", menu))
    app.add_handler(CallbackQueryHandler(menu_setting, pattern="^MENU_SETTING"))
    app.add_handler(CallbackQueryHandler(add_member, pattern="^ADD_MEMBER"))
    app.add_handler(CallbackQueryHandler(add_saldo, pattern="^ADD_SALDO"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_member))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_saldo))

    print("✅ Bot Connected!")
    app.run_polling()

if __name__ == "__main__":
    main()
