# ============================
# BOT MULTITOOLS - YINN VPN
# BAGIAN 1 - ATAS
# ============================

import logging
import sqlite3
import os
import requests
import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, CallbackQueryHandler, ContextTypes
)

# ----------------------------
# KONFIGURASI BOT
# ----------------------------
BOT_TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"
ADMIN_ID = 6353421952
DB_FILE = "users.db"

# ----------------------------
# SETUP LOGGING
# ----------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ----------------------------
# DATABASE USER
# ----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        join_date TEXT
    )''')
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        join_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, username, join_date))
        conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    conn.close()
    return data

# Inisialisasi database
init_db()
# ============================
# BOT MULTITOOLS - YINN VPN
# BAGIAN 2 - MENU UTAMA & START
# ============================

# ----------------------------
# FUNGSI MENU UTAMA
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)

    # Menu utama
    keyboard = [
        [InlineKeyboardButton("📜 All Menu", callback_data="all_menu")],
        [InlineKeyboardButton("📩 Contact Admin", url="https://t.me/yinnprovpn")],
    ]

    # Tombol admin hanya untuk ADMIN_ID
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Selamat datang {user.first_name} di bot MultiTools by Yinn VPN!\n"
        "Gunakan bot ini dengan bijak. Pilih menu di bawah untuk memulai:",
        reply_markup=reply_markup
    )

# ----------------------------
# HANDLER MENU UTAMA
# ----------------------------
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔗 AdBypass", callback_data="ad_bypass")],
        [InlineKeyboardButton("🌐 Proxy Checker", callback_data="proxy_checker")],
        [InlineKeyboardButton("🛡️ Check SSL", callback_data="check_ssl")],
        [InlineKeyboardButton("📌 IP Lookup", callback_data="ip_lookup")],
        [InlineKeyboardButton("🔍 Server Port Scanner", callback_data="port_scanner")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="back_home")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📜 Berikut daftar fitur bot ini:",
        reply_markup=reply_markup
    )

# ----------------------------
# HANDLER TOMBOL KEMBALI
# ----------------------------
async def back_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("📜 All Menu", callback_data="all_menu")],
        [InlineKeyboardButton("📩 Contact Admin", url="https://t.me/yinnprovpn")],
    ]
    if query.from_user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("🛠️ Admin Panel", callback_data="admin_panel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "🏠 Kembali ke menu utama:",
        reply_markup=reply_markup
    )

# ----------------------------
# REGISTER HANDLER UTAMA
# ----------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(main_menu, pattern="all_menu"))
app.add_handler(CallbackQueryHandler(back_home, pattern="back_home"))
# ============================
# BOT MULTITOOLS - YINN VPN
# BAGIAN 3 - SEMUA FITUR
# ============================

# ----------------------------
# 1️⃣ FITUR ADBYPASS
# ----------------------------
async def menu_adbypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔗 Bypass Link", callback_data="adbypass_link")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")],
    ]
    await query.edit_message_text("🔗 Fitur AdBypass:\nGunakan untuk melewati link shortener.", reply_markup=InlineKeyboardMarkup(keyboard))

async def adbypass_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("⚡ Masukkan link yang ingin di-bypass:")
    context.user_data["wait_bypass"] = True

async def process_adbypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("wait_bypass"):
        url = update.message.text
        msg = await update.message.reply_text("⏳ Sedang memproses...")
        try:
            api = "https://bypass.vip/api?url=" + url
            result = requests.get(api, timeout=10).json()
            if result.get("success"):
                await msg.edit_text(f"✅ Link berhasil di-bypass:\n{result['destination']}")
            else:
                await msg.edit_text("❌ Gagal bypass link, coba link lain.")
        except:
            await msg.edit_text("⚠️ Terjadi kesalahan server.")
        context.user_data["wait_bypass"] = False
        await update.message.delete()

# ----------------------------
# 2️⃣ PROXY CHECKER
# ----------------------------
async def menu_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌐 Cek Proxy", callback_data="proxy_check_input")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")],
    ]
    await query.edit_message_text("🌐 Masukkan proxy dalam format:\n`ip:port`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def proxy_check_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("🌐 Kirim proxy yang ingin dicek (format ip:port):")
    context.user_data["wait_proxy"] = True

async def process_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("wait_proxy"):
        proxy = update.message.text.strip()
        msg = await update.message.reply_text("🔍 Mengecek proxy...")
        try:
            ip, port = proxy.split(":")
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip, int(port)))
            if result == 0:
                await msg.edit_text("✅ Proxy aktif dan dapat digunakan.")
            else:
                await msg.edit_text("❌ Proxy tidak merespon.")
            sock.close()
        except:
            await msg.edit_text("⚠️ Format salah atau proxy error.")
        context.user_data["wait_proxy"] = False
        await update.message.delete()

# ----------------------------
# 3️⃣ CHECK SSL
# ----------------------------
async def menu_ssl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛡️ Cek SSL Domain", callback_data="ssl_input")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")],
    ]
    await query.edit_message_text("🛡️ Masukkan domain untuk cek SSL:", reply_markup=InlineKeyboardMarkup(keyboard))

async def ssl_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("🛡️ Kirim domain yang ingin dicek (contoh: google.com):")
    context.user_data["wait_ssl"] = True

async def process_ssl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("wait_ssl"):
        domain = update.message.text.strip()
        msg = await update.message.reply_text("🔎 Mengecek SSL...")
        try:
            api = f"https://api.ssllabs.com/api/v3/analyze?host={domain}"
            res = requests.get(api, timeout=15).json()
            if "host" in res:
                await msg.edit_text(f"✅ SSL valid untuk: {res['host']}")
            else:
                await msg.edit_text("❌ SSL tidak valid atau domain tidak ditemukan.")
        except:
            await msg.edit_text("⚠️ Gagal mengecek SSL.")
        context.user_data["wait_ssl"] = False
        await update.message.delete()

# ----------------------------
# 4️⃣ IP LOOKUP
# ----------------------------
async def menu_iplookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📌 Cek IP", callback_data="ip_input")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")],
    ]
    await query.edit_message_text("📌 Masukkan alamat IP untuk lookup:", reply_markup=InlineKeyboardMarkup(keyboard))

async def ip_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("📌 Kirim IP yang ingin dicek:")
    context.user_data["wait_ip"] = True

async def process_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("wait_ip"):
        ip = update.message.text.strip()
        msg = await update.message.reply_text("🔎 Mengecek IP...")
        try:
            res = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
            if res.get("status") == "success":
                info = (
                    f"🌍 IP: {res['query']}\n"
                    f"🔹 Negara: {res['country']}\n"
                    f"🔹 Kota: {res['city']}\n"
                    f"🔹 ISP: {res['isp']}"
                )
                await msg.edit_text(info)
            else:
                await msg.edit_text("❌ IP tidak valid.")
        except:
            await msg.edit_text("⚠️ Gagal mendapatkan data IP.")
        context.user_data["wait_ip"] = False
        await update.message.delete()

# ----------------------------
# 5️⃣ PORT SCANNER
# ----------------------------
async def menu_portscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔍 Scan Port", callback_data="port_input")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")],
    ]
    await query.edit_message_text("🔍 Masukkan IP atau domain untuk scan port:", reply_markup=InlineKeyboardMarkup(keyboard))

async def port_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("🔍 Kirim target untuk scan port (contoh: google.com):")
    context.user_data["wait_port"] = True

async def process_portscan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("wait_port"):
        target = update.message.text.strip()
        msg = await update.message.reply_text("⏳ Scanning port 80, 443, 22...")
        open_ports = []
        try:
            import socket
            for port in [80, 443, 22]:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                s.close()
            if open_ports:
                await msg.edit_text(f"✅ Port terbuka: {', '.join(map(str, open_ports))}")
            else:
                await msg.edit_text("❌ Tidak ada port terbuka.")
        except:
            await msg.edit_text("⚠️ Gagal scan port.")
        context.user_data["wait_port"] = False
        await update.message.delete()
# ============================
# BOT MULTITOOLS - YINN VPN
# BAGIAN 4 - ADMIN PANEL & SISTEM
# ============================

# ----------------------------
# ADMIN MENU
# ----------------------------
ADMIN_ID = 6353421952

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("👥 Cek User List", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Kirim Pengumuman", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="main_menu")],
    ]
    await query.edit_message_text("⚙️ **Admin Panel**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

# ----------------------------
# CEK USER LIST
# ----------------------------
async def admin_userlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.callback_query.answer("❌ Akses ditolak.", show_alert=True)

    text = "📜 **Daftar Pengguna Bot:**\n\n"
    for uid, info in user_data.items():
        text += f"👤 {info['username']} | 🆔 `{uid}` | 📅 {info['joined']}\n"
    if not user_data:
        text = "⚠️ Belum ada pengguna yang tercatat."
    await update.callback_query.edit_message_text(text, parse_mode="Markdown")

# ----------------------------
# KIRIM PENGUMUMAN
# ----------------------------
async def admin_broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.callback_query.answer("❌ Akses ditolak.", show_alert=True)

    await update.callback_query.message.reply_text("📢 Kirim pesan pengumuman yang ingin dibagikan (support text, foto, sticker).")
    context.user_data["wait_broadcast"] = True

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.user_data.get("wait_broadcast"):
        count = 0
        for uid in user_data:
            try:
                if update.message.text:
                    await context.bot.send_message(uid, f"📢 **Pengumuman:**\n{update.message.text}", parse_mode="Markdown")
                elif update.message.photo:
                    await context.bot.send_photo(uid, update.message.photo[-1].file_id, caption="📢 Pengumuman dari Admin")
                elif update.message.sticker:
                    await context.bot.send_sticker(uid, update.message.sticker.file_id)
                count += 1
            except:
                pass
        await update.message.reply_text(f"✅ Pengumuman terkirim ke {count} pengguna.")
        context.user_data["wait_broadcast"] = False

# ----------------------------
# AUTO DELETE HANDLER
# ----------------------------
async def auto_delete(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=context.job.chat_id, message_id=context.job.message_id)
    except:
        pass

async def schedule_delete(message):
    job_queue.run_once(auto_delete, 10, chat_id=message.chat_id, name=str(message.message_id), data=None)
    job_queue.jobs()[-1].message_id = message.message_id

# ----------------------------
# CALLBACK HANDLER
# ----------------------------
application.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
application.add_handler(CallbackQueryHandler(all_menu, pattern="all_menu"))
application.add_handler(CallbackQueryHandler(contact_admin, pattern="contact_admin"))
application.add_handler(CallbackQueryHandler(admin_menu, pattern="admin_menu"))
application.add_handler(CallbackQueryHandler(admin_userlist, pattern="admin_users"))
application.add_handler(CallbackQueryHandler(admin_broadcast_menu, pattern="admin_broadcast"))

application.add_handler(CallbackQueryHandler(menu_adbypass, pattern="adbypass"))
application.add_handler(CallbackQueryHandler(adbypass_link, pattern="adbypass_link"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_adbypass))

application.add_handler(CallbackQueryHandler(menu_proxy, pattern="proxy"))
application.add_handler(CallbackQueryHandler(proxy_check_input, pattern="proxy_check_input"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_proxy))

application.add_handler(CallbackQueryHandler(menu_ssl, pattern="ssl"))
application.add_handler(CallbackQueryHandler(ssl_input, pattern="ssl_input"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_ssl))

application.add_handler(CallbackQueryHandler(menu_iplookup, pattern="iplookup"))
application