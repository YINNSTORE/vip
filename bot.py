import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import asyncio
import requests

# ==============================
# ✅ KONFIGURASI BOT
# ==============================
TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"
ADMIN_ID = 6353421952
ADMIN_USERNAME = "yinnprovpn"

# ==============================
# ✅ LOGGER
# ==============================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==============================
# ✅ DATA USER
# ==============================
user_data = {}

# ==============================
# ✅ MENU UTAMA
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data[user.id] = {"username": user.username, "joined": update.message.date}

    keyboard = [
        [InlineKeyboardButton("📜 𝘼𝙡𝙡 𝙈𝙚𝙣𝙪", callback_data="all_menu")],
        [InlineKeyboardButton("👤 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝘼𝙙𝙢𝙞𝙣", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton("🔑 𝘼𝙙𝙢𝙞𝙣 𝙋𝙖𝙣𝙚𝙡", callback_data="admin_menu")] if user.id == ADMIN_ID else []
    ]

    reply_markup = InlineKeyboardMarkup([btn for btn in keyboard if btn])
    await update.message.reply_text(
        "🤖 𝐒𝐞𝐥𝐚𝐦𝐚𝐭 𝐃𝐚𝐭𝐚𝐧𝐠 𝐝𝐢 𝐁𝐨𝐭 𝐌𝐮𝐥𝐭𝐢𝐓𝐨𝐨𝐥𝐬 𝐛𝐲 𝐘𝐢𝐧𝐧 𝐕𝐏𝐍\n\n"
        "Gunakan bot ini dengan bijak ✅\n"
        "Klik tombol di bawah untuk menampilkan menu:",
        reply_markup=reply_markup
    )

# ==============================
# ✅ ALL MENU
# ==============================
async def all_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🛠️ 𝐀𝐝𝐁𝐚𝐲𝐩𝐚𝐬𝐬", callback_data="ad_bypass_menu")],
        [InlineKeyboardButton("🌐 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩", callback_data="ip_lookup_menu")],
        [InlineKeyboardButton("🛡️ 𝐏𝐫𝐨𝐱𝐲 𝐂𝐡𝐞𝐜𝐤𝐞𝐫", callback_data="proxy_checker_menu")],
        [InlineKeyboardButton("🔍 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧 𝐅𝐢𝐧𝐝𝐞𝐫", callback_data="subdomain_menu")],
        [InlineKeyboardButton("🔐 𝐒𝐒𝐋 𝐂𝐡𝐞𝐜𝐤𝐞𝐫", callback_data="ssl_checker_menu")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐔𝐭𝐚𝐦𝐚", callback_data="main_menu")]
    ]
    await query.edit_message_text(
        "📜 𝐃𝐚𝐟𝐭𝐚𝐫 𝐅𝐢𝐭𝐮𝐫 𝐁𝐨𝐭:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ SUBMENU - AdBypass
# ==============================
async def ad_bypass_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔗 𝘽𝙖𝙮𝙥𝙖𝙨𝙨 𝙇𝙞𝙣𝙠", callback_data="bypass_link")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="panduan_adbypass")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐅𝐢𝐭𝐮𝐫", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🛠️ 𝐅𝐢𝐭𝐮𝐫: 𝐀𝐝𝐁𝐚𝐲𝐩𝐚𝐬𝐬\n"
        "Masukkan link yang ingin dibypass dan bot akan mencoba melewati halaman iklan otomatis.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ SUBMENU - IP Lookup
# ==============================
async def ip_lookup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔎 𝘾𝙚𝙠 𝙄𝙋", callback_data="cek_ip")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="panduan_iplookup")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐅𝐢𝐭𝐮𝐫", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🌐 𝐅𝐢𝐭𝐮𝐫: 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩\n"
        "Masukkan IP atau domain dan bot akan menampilkan informasi detail.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ SUBMENU - Proxy Checker
# ==============================
async def proxy_checker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛡️ 𝘾𝙚𝙠 𝙋𝙧𝙤𝙭𝙮", callback_data="cek_proxy")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="panduan_proxy")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐅𝐢𝐭𝐮𝐫", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🛡️ 𝐅𝐢𝐭𝐮𝐫: 𝐏𝐫𝐨𝐱𝐲 𝐂𝐡𝐞𝐜𝐤𝐞𝐫\n"
        "Masukkan proxy dan bot akan memeriksa statusnya.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ SUBMENU - Subdomain Finder
# ==============================
async def subdomain_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔍 𝙁𝙞𝙣𝙙 𝙎𝙪𝙗𝙙𝙤𝙢𝙖𝙞𝙣", callback_data="find_subdomain")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="panduan_subdomain")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐅𝐢𝐭𝐮𝐫", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🔍 𝐅𝐢𝐭𝐮𝐫: 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧 𝐅𝐢𝐧𝐝𝐞𝐫\n"
        "Masukkan domain dan bot akan mencari subdomain yang tersedia.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ SUBMENU - SSL Checker
# ==============================
async def ssl_checker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔐 𝘾𝙚𝙠 𝙎𝙎𝙇", callback_data="cek_ssl")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="panduan_ssl")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐅𝐢𝐭𝐮𝐫", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🔐 𝐅𝐢𝐭𝐮𝐫: 𝐒𝐒𝐋 𝐂𝐡𝐞𝐜𝐤𝐞𝐫\n"
        "Masukkan domain dan bot akan mengecek sertifikat SSL.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ MENU ADMIN
# ==============================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📋 𝐂𝐞𝐤 𝐔𝐬𝐞𝐫 𝐋𝐢𝐬𝐭", callback_data="cek_userlist")],
        [InlineKeyboardButton("📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭", callback_data="broadcast_menu")],
        [InlineKeyboardButton("⬅️ 𝐊𝐞 𝐌𝐞𝐧𝐮 𝐔𝐭𝐚𝐦𝐚", callback_data="main_menu")]
    ]
    await query.edit_message_text(
        "🔑 𝐌𝐞𝐧𝐮 𝐀𝐝𝐦𝐢𝐧",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==============================
# ✅ CALLBACK HANDLER MENU
# ==============================
def register_part1_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(all_menu, pattern="all_menu"))
    app.add_handler(CallbackQueryHandler(ad_bypass_menu, pattern="ad_bypass_menu"))
    app.add_handler(CallbackQueryHandler(ip_lookup_menu, pattern="ip_lookup_menu"))
    app.add_handler(CallbackQueryHandler(proxy_checker_menu, pattern="proxy_checker_menu"))
    app.add_handler(CallbackQueryHandler(subdomain_menu, pattern="subdomain_menu"))
    app.add_handler(CallbackQueryHandler(ssl_checker_menu, pattern="ssl_checker_menu"))
    app.add_handler(CallbackQueryHandler(admin_menu, pattern="admin_menu"))

import os
import socket
import ssl
from telegram.constants import ParseMode

# ==============================
# ✅ FUNGSI - Ad Bypass
# ==============================
async def bypass_link_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔗 𝐊𝐢𝐫𝐢𝐦 𝐥𝐢𝐧𝐤 𝐲𝐚𝐧𝐠 𝐢𝐧𝐠𝐢𝐧 𝐝𝐢𝐛𝐚𝐲𝐩𝐚𝐬𝐬...")

async def handle_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    # Sementara dummy response karena beberapa link tidak support bypass otomatis
    await update.message.reply_text(f"✅ 𝐇𝐚𝐬𝐢𝐥 𝐁𝐚𝐲𝐩𝐚𝐬𝐬:\n\n🔗 {link}")

# ==============================
# ✅ FUNGSI - IP Lookup (dengan API Key yang kamu kasih)
# ==============================
IPINFO_API = "210a01b5fe3d19"

async def cek_ip_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 𝐊𝐢𝐫𝐢𝐦 𝐀𝐥𝐚𝐦𝐚𝐭 𝐈𝐏 𝐚𝐭𝐚𝐮 𝐃𝐨𝐦𝐚𝐢𝐧...")

async def handle_iplookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.text.strip()
    try:
        resp = requests.get(f"https://ipinfo.io/{target}?token={IPINFO_API}")
        data = resp.json()
        result = (
            f"🌐 𝐇𝐚𝐬𝐢𝐥 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩\n"
            f"• IP: {data.get('ip','-')}\n"
            f"• Hostname: {data.get('hostname','-')}\n"
            f"• Org: {data.get('org','-')}\n"
            f"• Country: {data.get('country','-')}\n"
            f"• Region: {data.get('region','-')}\n"
            f"• City: {data.get('city','-')}\n"
        )
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text("❌ 𝐆𝐚𝐠𝐚𝐥 𝐦𝐞𝐦𝐩𝐫𝐨𝐬𝐞𝐬 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩.")

# ==============================
# ✅ FUNGSI - Proxy Checker
# ==============================
async def cek_proxy_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ 𝐊𝐢𝐫𝐢𝐦 𝐏𝐫𝐨𝐱𝐲 (𝐟𝐨𝐫𝐦𝐚𝐭: ip:port)...")

async def handle_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proxy = update.message.text.strip()
    try:
        ip, port = proxy.split(":")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((ip, int(port)))
        if result == 0:
            await update.message.reply_text(f"✅ 𝐏𝐫𝐨𝐱𝐲 {proxy} 𝐀𝐤𝐭𝐢𝐟")
        else:
            await update.message.reply_text(f"❌ 𝐏𝐫𝐨𝐱𝐲 {proxy} 𝐌𝐚𝐭𝐢")
        s.close()
    except:
        await update.message.reply_text("⚠️ 𝐏𝐞𝐫𝐢𝐤𝐬𝐚 𝐟𝐨𝐫𝐦𝐚𝐭 𝐩𝐫𝐨𝐱𝐲.")

# ==============================
# ✅ FUNGSI - Subdomain Finder (Anubis)
# ==============================
async def find_subdomain_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 𝐊𝐢𝐫𝐢𝐦 𝐝𝐨𝐦𝐚𝐢𝐧 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐧𝐜𝐚𝐫𝐢 𝐬𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧...")

async def handle_subdomain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.strip()
    try:
        url = f"https://jldc.me/anubis/subdomains/{domain}"
        r = requests.get(url, timeout=10)
        subs = r.json()
        if not subs:
            await update.message.reply_text("❌ 𝐓𝐢𝐝𝐚𝐤 𝐦𝐞𝐧𝐞𝐦𝐮𝐤𝐚𝐧 𝐬𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧.")
            return
        hasil = "\n".join(subs)
        await update.message.reply_text(f"🔍 𝐇𝐚𝐬𝐢𝐥 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧:\n{hasil}")
    except:
        await update.message.reply_text("⚠️ 𝐆𝐚𝐠𝐚𝐥 𝐦𝐞𝐧𝐜𝐚𝐫𝐢 𝐬𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧.")

# ==============================
# ✅ FUNGSI - SSL Checker
# ==============================
async def cek_ssl_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 𝐊𝐢𝐫𝐢𝐦 𝐝𝐨𝐦𝐚𝐢𝐧 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐧𝐠𝐞𝐜𝐞𝐤 𝐒𝐒𝐋...")

async def handle_ssl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    domain = update.message.text.strip()
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain, 443))
            cert = s.getpeercert()
            issuer = dict(x[0] for x in cert['issuer'])
            subject = dict(x[0] for x in cert['subject'])
            valid_from = cert['notBefore']
            valid_to = cert['notAfter']
            result = (
                f"🔐 𝐒𝐒𝐋 𝐂𝐡𝐞𝐜𝐤 𝐇𝐚𝐬𝐢𝐥\n"
                f"• Issuer: {issuer.get('organizationName','-')}\n"
                f"• Subject: {subject.get('commonName','-')}\n"
                f"• Berlaku dari: {valid_from}\n"
                f"• Berlaku sampai: {valid_to}"
            )
            await update.message.reply_text(result)
    except:
        await update.message.reply_text("⚠️ 𝐆𝐚𝐠𝐚𝐥 𝐦𝐞𝐧𝐠𝐞𝐜𝐞𝐤 𝐒𝐒𝐋.")

# ==============================
# ✅ ADMIN PANEL (User List + Broadcast)
# ==============================
async def cek_userlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    teks = "📋 𝐃𝐚𝐟𝐭𝐚𝐫 𝐔𝐬𝐞𝐫:\n"
    for uid, info in user_data.items():
        teks += f"• {info['username']} ({uid})\n"
    await update.callback_query.message.reply_text(teks)

async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📢 𝐊𝐢𝐫𝐢𝐦 𝐩𝐞𝐬𝐚𝐧 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐬𝐞𝐤𝐚𝐫𝐚𝐧𝐠:")

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    pesan = update.message.text
    for uid in user_data:
        try:
            await context.bot.send_message(uid, pesan)
        except:
            pass
    await update.message.reply_text("✅ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐬𝐮𝐝𝐚𝐡 𝐝𝐢𝐤𝐢𝐫𝐢𝐦.")

# ==============================
# ✅ REGISTER HANDLERS
# ==============================
def register_part2_handlers(app):
    # Fungsi
    app.add_handler(CallbackQueryHandler(bypass_link_func, pattern="bypass_link"))
    app.add_handler(CallbackQueryHandler(cek_ip_func, pattern="cek_ip"))
    app.add_handler(CallbackQueryHandler(cek_proxy_func, pattern="cek_proxy"))
    app.add_handler(CallbackQueryHandler(find_subdomain_func, pattern="find_subdomain"))
    app.add_handler(CallbackQueryHandler(cek_ssl_func, pattern="cek_ssl"))
    app.add_handler(CallbackQueryHandler(cek_userlist, pattern="cek_userlist"))
    app.add_handler(CallbackQueryHandler(broadcast_menu, pattern="broadcast_menu"))
    
    # Input teks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bypass))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_iplookup))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_proxy))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subdomain))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ssl))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))