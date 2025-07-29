# ===========================
# 📌 BOT MULTITOOLS BY YINN VPN
# FULL SYSTEM VERSION FIXED
# ===========================

import logging
import requests
import asyncio
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ===========================
# CONFIG
# ===========================
BOT_TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"
ADMIN_ID = 6353421952

# ===========================
# LOGGING
# ===========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ===========================
# START APPLICATION
# ===========================
application = ApplicationBuilder().token(BOT_TOKEN).build()
job_queue = application.job_queue

# ===========================
# USER DATABASE
# ===========================
users_data = {}  # {user_id: {"username": str, "join_date": datetime}}

# ===========================
# MAIN MENU
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Tidak ada username"
    if user_id not in users_data:
        users_data[user_id] = {
            "username": username,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    keyboard = [
        [InlineKeyboardButton("📂 All Menu", callback_data="all_menu")],
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/yinnvpn")],
        [InlineKeyboardButton("⚙️ Admin Menu", callback_data="admin_menu")] if user_id == ADMIN_ID else []
    ]
    reply_markup = InlineKeyboardMarkup([btn for btn in keyboard if btn])
    await update.message.reply_text(
        "Selamat datang di bot multitools by Yinn VPN!\nGunakan bot ini dengan bijak.",
        reply_markup=reply_markup
    )

# ===========================
# ALL MENU
# ===========================
async def all_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔗 AdBypass", callback_data="ad_bypass")],
        [InlineKeyboardButton("🔍 IP Lookup", callback_data="ip_lookup")],
        [InlineKeyboardButton("🌐 Proxy Checker", callback_data="proxy_checker")],
        [InlineKeyboardButton("🔐 SSL Checker", callback_data="ssl_checker")],
        [InlineKeyboardButton("📌 Server Status", callback_data="server_status")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    await update.callback_query.edit_message_text(
        "Pilih fitur yang tersedia:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===========================
# MENU ADMIN
# ===========================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👥 Cek User List", callback_data="cek_user")],
        [InlineKeyboardButton("📢 Kirim Pengumuman", callback_data="broadcast")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    await update.callback_query.edit_message_text(
        "⚙️ Menu Admin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===========================
# HANDLER BUTTON CALLBACK
# ===========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "main_menu":
        await start(update, context)
    elif data == "all_menu":
        await all_menu(update, context)
    elif data == "admin_menu":
        await admin_menu(update, context)
    elif data == "cek_user":
        text = "📋 Daftar Pengguna Bot:\n"
        for uid, info in users_data.items():
            text += f"• ID: `{uid}` | @{info['username']} | Bergabung: {info['join_date']}\n"
        await query.edit_message_text(text or "Belum ada pengguna.")
    elif data == "ad_bypass":
        await query.edit_message_text("🔗 Kirim link yang ingin di-bypass:")
        context.user_data["mode"] = "ad_bypass"
    elif data == "ip_lookup":
        await query.edit_message_text("🔍 Kirim IP/domain untuk dicek:")
        context.user_data["mode"] = "ip_lookup"
    elif data == "proxy_checker":
        await query.edit_message_text("🌐 Kirim IP:PORT proxy untuk dicek:")
        context.user_data["mode"] = "proxy_checker"
    elif data == "ssl_checker":
        await query.edit_message_text("🔐 Kirim domain untuk cek SSL:")
        context.user_data["mode"] = "ssl_checker"
    elif data == "server_status":
        await query.edit_message_text("✅ Server sedang online dan berjalan normal.")

# ===========================
# HANDLE PESAN USER
# ===========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    text = update.message.text

    # Auto delete setelah 5 detik
    asyncio.create_task(delete_message(update, 5))

    if not mode:
        return

    if mode == "ad_bypass":
        if "http" not in text:
            await update.message.reply_text("❌ Link tidak valid!")
            return
        await update.message.reply_text(f"✅ Link berhasil dibypass:\n{text} (simulasi)")  

    elif mode == "ip_lookup":
        try:
            r = requests.get(f"http://ip-api.com/json/{text}").json()
            if r["status"] == "fail":
                await update.message.reply_text("❌ IP/domain tidak ditemukan.")
            else:
                hasil = (f"📌 Hasil IP Lookup:\n"
                         f"IP: {r['query']}\nNegara: {r['country']}\nISP: {r['isp']}")
                await update.message.reply_text(hasil)
        except:
            await update.message.reply_text("⚠️ Gagal memproses IP lookup.")

    elif mode == "proxy_checker":
        await update.message.reply_text("🔄 Mengecek proxy...")
        await asyncio.sleep(2)
        if ":" not in text:
            await update.message.reply_text("❌ Format proxy salah. Gunakan IP:PORT")
        else:
            await update.message.reply_text("✅ Proxy aktif dan dapat digunakan. (simulasi)")

    elif mode == "ssl_checker":
        if "." not in text:
            await update.message.reply_text("❌ Domain tidak valid.")
        else:
            await update.message.reply_text(f"✅ SSL domain {text} masih berlaku. (simulasi)")

# ===========================
# AUTO DELETE
# ===========================
async def delete_message(update, delay: int):
    await asyncio.sleep(delay)
    try:
        await update.message.delete()
    except:
        pass

# ===========================
# BROADCAST ADMIN
# ===========================
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text or ""
    for uid in users_data.keys():
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Pengumuman:\n{text}")
        except:
            pass

# ===========================
# REGISTER HANDLER
# ===========================
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))

# ===========================
# RUN BOT
# ===========================
print("✅ Bot Multitools berjalan...")
application.run_polling()