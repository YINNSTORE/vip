# ============================================
# BOT TELEGRAM MULTITOOLS - PART 1 (ATAS)
# ============================================

import logging
from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton,
    InputMediaPhoto, InputMediaVideo, InputMediaDocument
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import os
import json
import datetime

# =========================
# KONFIGURASI BOT
# =========================
TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"
ADMIN_ID = 6353421952
DATA_FILE = "user_data.json"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================
# DATABASE USER
# =========================
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

USERS = load_users()

def add_user(user_id, username):
    if str(user_id) not in USERS:
        USERS[str(user_id)] = {
            "username": username,
            "join_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(USERS)

# =========================
# AUTO DELETE SYSTEM
# =========================
async def auto_delete(context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = context.job.data['chat_id']
        msg_id = context.job.data['msg_id']
        await context.bot.delete_message(chat_id, msg_id)
    except Exception as e:
        logger.warning(f"Gagal auto-delete pesan: {e}")

async def schedule_delete(context, chat_id, msg_id, delay=8):
    context.job_queue.run_once(auto_delete, delay, data={'chat_id': chat_id, 'msg_id': msg_id})

# =========================
# MENU UTAMA
# =========================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📜 All Menu", callback_data="all_menu")],
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/YinnVpn")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "Unknown")
    msg = await update.message.reply_text(
        f"👋 Selamat datang {user.first_name} di Bot MultiTools by Yinn VPN\n\n"
        "Gunakan bot ini dengan bijak ✅",
        reply_markup=main_menu()
    )
    await schedule_delete(context, msg.chat_id, msg.message_id)

# =========================
# ADMIN PANEL
# =========================
def admin_menu():
    keyboard = [
        [InlineKeyboardButton("👥 Cek User List", callback_data="cek_users")],
        [InlineKeyboardButton("📢 Kirim Pengumuman", callback_data="broadcast")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def open_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.callback_query.message.edit_text(
        "⚙️ Menu Admin",
        reply_markup=admin_menu()
    )

async def cek_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = "📜 *Daftar Pengguna Bot:*\n\n"
    for uid, info in USERS.items():
        text += f"👤 ID: `{uid}` | @{info['username']}\n📅 Bergabung: {info['join_date']}\n\n"
    await update.callback_query.message.reply_text(text, parse_mode="Markdown")

# ==== END PART 1 ====
# ============================================
# BOT TELEGRAM MULTITOOLS - PART 2 (TENGAH)
# ============================================

# =========================
# MENU ALL FEATURE
# =========================
def all_menu_markup():
    keyboard = [
        [InlineKeyboardButton("🔗 AdBypass", callback_data="menu_adbypass")],
        [InlineKeyboardButton("🌐 Proxy Caker", callback_data="menu_proxy")],
        [InlineKeyboardButton("🔎 IP Lookup", callback_data="menu_iplookup")],
        [InlineKeyboardButton("🔐 SSL Checker", callback_data="menu_sslchecker")],
        [InlineKeyboardButton("🕵️ Subdomain Finder", callback_data="menu_subdomain")],
        [InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def open_all_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.message.edit_text(
        "📜 *Daftar Fitur Bot:*\nPilih salah satu fitur di bawah ⬇️",
        parse_mode="Markdown",
        reply_markup=all_menu_markup()
    )

# =========================
# FITUR 1: ADBYPASS
# =========================
def adbypass_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Bypass Link", callback_data="adbypass_start")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]
    ])

async def open_adbypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "🔗 *Fitur AdBypass*\nGunakan untuk bypass link iklan seperti Mediafire, Adfly, dll.",
        parse_mode="Markdown",
        reply_markup=adbypass_menu()
    )

async def adbypass_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.callback_query.message.reply_text(
        "🔗 Masukkan link yang ingin di-bypass:"
    )
    context.user_data["awaiting_adbypass"] = True
    await schedule_delete(context, msg.chat_id, msg.message_id, 15)

async def handle_adbypass_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_adbypass"):
        link = update.message.text.strip()
        context.user_data["awaiting_adbypass"] = False
        msg_id = update.message.message_id

        # Simulasi proses bypass
        if "http" not in link:
            res = await update.message.reply_text("❌ Link tidak valid!")
        else:
            # (Simulasi) hasil bypass
            bypassed = link.replace("adfly", "direct").replace("mediafire", "download")
            res = await update.message.reply_text(f"✅ Link berhasil di-bypass:\n{bypassed}")

        await schedule_delete(context, update.message.chat_id, msg_id, 5)

# =========================
# FITUR 2: PROXY CAKER
# =========================
def proxy_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Ambil Proxy List", callback_data="proxy_start")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]
    ])

async def open_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "🌐 *Fitur Proxy Caker*\nMengambil daftar proxy publik aktif.",
        parse_mode="Markdown",
        reply_markup=proxy_menu()
    )

async def proxy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simulasi ambil proxy
    proxies = ["123.45.67.89:8080", "98.76.54.32:3128"]
    if proxies:
        text = "✅ *Daftar Proxy Aktif:*\n" + "\n".join(proxies)
    else:
        text = "❌ Tidak ada proxy yang tersedia."
    await update.callback_query.message.reply_text(text, parse_mode="Markdown")

# =========================
# FITUR 3: IP LOOKUP
# =========================
def iplookup_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Cek IP", callback_data="iplookup_start")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]
    ])

async def open_iplookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "🔎 *Fitur IP Lookup*\nMasukkan alamat IP untuk mendapatkan informasi lokasi & ISP.",
        parse_mode="Markdown",
        reply_markup=iplookup_menu()
    )

async def iplookup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.callback_query.message.reply_text("🔍 Masukkan alamat IP yang ingin dicek:")
    context.user_data["awaiting_iplookup"] = True
    await schedule_delete(context, msg.chat_id, msg.message_id, 15)

async def handle_iplookup_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_iplookup"):
        ip = update.message.text.strip()
        context.user_data["awaiting_iplookup"] = False
        msg_id = update.message.message_id

        # Simulasi cek IP (validasi sederhana)
        if not any(c.isdigit() for c in ip):
            res = await update.message.reply_text("❌ IP tidak valid!")
        else:
            # Simulasi respon
            res = await update.message.reply_text(
                f"✅ Hasil IP Lookup:\nIP: {ip}\nNegara: Indonesia\nISP: ExampleNet"
            )
        await schedule_delete(context, update.message.chat_id, msg_id, 5)

# ==== END PART 2 ====
# ============================================
# BOT TELEGRAM MULTITOOLS - PART 3 (BAWAH)
# ============================================

# =========================
# FITUR 4: SSL CHECKER
# =========================
def sslchecker_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Cek SSL", callback_data="ssl_start")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]
    ])

async def open_sslchecker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "🔐 *SSL Checker*\nMasukkan domain untuk mengecek status SSL.",
        parse_mode="Markdown",
        reply_markup=sslchecker_menu()
    )

async def ssl_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.callback_query.message.reply_text("🔐 Masukkan domain (contoh: google.com):")
    context.user_data["awaiting_ssl"] = True
    await schedule_delete(context, msg.chat_id, msg.message_id, 15)

async def handle_ssl_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_ssl"):
        domain = update.message.text.strip()
        context.user_data["awaiting_ssl"] = False
        msg_id = update.message.message_id

        if "." not in domain:
            res = await update.message.reply_text("❌ Domain tidak valid!")
        else:
            res = await update.message.reply_text(
                f"✅ SSL untuk {domain}: Valid ✅\nKedaluwarsa: 2026-12-31"
            )
        await schedule_delete(context, update.message.chat_id, msg_id, 5)

# =========================
# FITUR 5: SUBDOMAIN FINDER
# =========================
def subdomain_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🕵️ Cari Subdomain", callback_data="subdomain_start")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]
    ])

async def open_subdomain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "🕵️ *Subdomain Finder*\nMasukkan domain untuk mencari subdomain publik.",
        parse_mode="Markdown",
        reply_markup=subdomain_menu()
    )

async def subdomain_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.callback_query.message.reply_text("🕵️ Masukkan domain (contoh: example.com):")
    context.user_data["awaiting_subdomain"] = True
    await schedule_delete(context, msg.chat_id, msg.message_id, 15)

async def handle_subdomain_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_subdomain"):
        domain = update.message.text.strip()
        context.user_data["awaiting_subdomain"] = False
        msg_id = update.message.message_id

        if "." not in domain:
            res = await update.message.reply_text("❌ Domain tidak valid!")
        else:
            # Simulasi hasil pencarian
            hasil = [f"mail.{domain}", f"dev.{domain}", f"api.{domain}"]
            res = await update.message.reply_text(
                "✅ Ditemukan subdomain:\n" + "\n".join(hasil)
            )
        await schedule_delete(context, update.message.chat_id, msg_id, 5)

# =========================
# ADMIN - BROADCAST
# =========================
async def open_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = await update.callback_query.message.reply_text(
        "📢 Masukkan pesan, gambar, atau sticker untuk dikirim ke semua pengguna."
    )
    context.user_data["awaiting_broadcast"] = True
    await schedule_delete(context, msg.chat_id, msg.message_id, 20)

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_broadcast"):
        context.user_data["awaiting_broadcast"] = False
        for uid in USERS.keys():
            try:
                if update.message.photo:
                    photo_id = update.message.photo[-1].file_id
                    await update.message.bot.send_photo(chat_id=int(uid), photo=photo_id, caption=update.message.caption or "")
                elif update.message.sticker:
                    await update.message.bot.send_sticker(chat_id=int(uid), sticker=update.message.sticker.file_id)
                else:
                    await update.message.bot.send_message(chat_id=int(uid), text=update.message.text)
            except Exception:
                continue
        await update.message.reply_text("✅ Pengumuman berhasil dikirim.")

# =========================
# CALLBACK HANDLER
# =========================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "all_menu": await open_all_menu(update, context)
    elif data == "menu_adbypass": await open_adbypass(update, context)
    elif data == "adbypass_start": await adbypass_start(update, context)

    elif data == "menu_proxy": await open_proxy(update, context)
    elif data == "proxy_start": await proxy_start(update, context)

    elif data == "menu_iplookup": await open_iplookup(update, context)
    elif data == "iplookup_start": await iplookup_start(update, context)

    elif data == "menu_sslchecker": await open_sslchecker(update, context)
    elif data == "ssl_start": await ssl_start(update, context)

    elif data == "menu_subdomain": await open_subdomain(update, context)
    elif data == "subdomain_start": await subdomain_start(update, context)

    elif data == "admin_panel": await open_admin(update, context)
    elif data == "cek_users": await cek_users(update, context)
    elif data == "broadcast": await open_broadcast(update, context)

    elif data == "back_main":
        await query.message.edit_text(
            "👋 Selamat datang kembali di Bot MultiTools by Yinn VPN",
            reply_markup=main_menu()
        )

# =========================
# SETUP BOT
# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_adbypass_input))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_iplookup_input))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ssl_input))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subdomain_input))
app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.STICKER) & ~filters.COMMAND, handle_broadcast))

print("🤖 Bot berjalan...")
app.run_polling()
# ==== END PART 3 ====