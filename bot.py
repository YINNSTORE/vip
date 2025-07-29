# ==================== [ BOT MULTITOOLS - BAGIAN 1 / 3 ] ====================
# ✅ Developer : YinnVPN
# ✅ Admin ID  : 6353421952
# ✅ Bot Token : 7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg
# ✅ Revisi : Font teks & tombol, menu tombol terstruktur, submenu, emoji tidak dihapus

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import logging

# ====== LOGGING ======
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ====== ID ADMIN ======
ADMIN_ID = 6353421952

# ====== START COMMAND ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pesan awal bot"""
    keyboard = [
        [InlineKeyboardButton("📜 𝘼𝙡𝙡 𝙈𝙚𝙣𝙪", callback_data="all_menu")],
        [InlineKeyboardButton("👤 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝘼𝙙𝙢𝙞𝙣", url="https://t.me/yinnprovpn")],
        [InlineKeyboardButton("🛠️ 𝘼𝙙𝙢𝙞𝙣 𝙈𝙚𝙣𝙪", callback_data="admin_menu")] if update.effective_user.id == ADMIN_ID else [] 
    ]

    reply_markup = InlineKeyboardMarkup([btn for btn in keyboard if btn])
    
    await update.message.reply_text(
        "👋 𝐒𝐞𝐥𝐚𝐦𝐚𝐭 𝐝𝐚𝐭𝐚𝐧𝐠 𝐝𝐢 𝐛𝐨𝐭 𝐦𝐮𝐥𝐭𝐢𝐭𝐨𝐨𝐥𝐬 𝐛𝐲 𝐘𝐢𝐧𝐧 𝐕𝐏𝐍\n"
        "⚠️ 𝐆𝐮𝐧𝐚𝐤𝐚𝐧 𝐛𝐨𝐭 𝐢𝐧𝐢 𝐝𝐞𝐧𝐠𝐚𝐧 𝐛𝐢𝐣𝐚𝐤\n\n"
        "📌 𝐏𝐢𝐥𝐢𝐡 𝐦𝐞𝐧𝐮 𝐝𝐢 𝐛𝐚𝐰𝐚𝐡 𝐢𝐧𝐢 ⬇️",
        reply_markup=reply_markup
    )

# ====== HANDLER ALL MENU ======
async def all_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan semua fitur utama"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🔗 𝘼𝙙 𝘽𝙖𝙮𝙥𝙖𝙨𝙨", callback_data="ad_bypass_menu")],
        [InlineKeyboardButton("🌐 𝙄𝙋 𝙇𝙤𝙤𝙠𝙪𝙥", callback_data="ip_lookup_menu")],
        [InlineKeyboardButton("🛡️ 𝙋𝙧𝙤𝙭𝙮 𝘾𝙝𝙚𝙘𝙠𝙚𝙧", callback_data="proxy_checker_menu")],
        [InlineKeyboardButton("🕵️ 𝙎𝙪𝙗𝙙𝙤𝙢𝙖𝙞𝙣 𝙁𝙞𝙣𝙙𝙚𝙧", callback_data="subdomain_finder_menu")],
        [InlineKeyboardButton("🔐 𝙎𝙎𝙇 𝘾𝙝𝙚𝙘𝙠", callback_data="ssl_check_menu")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "📜 𝐌𝐞𝐧𝐮 𝐔𝐭𝐚𝐦𝐚\n"
        "📌 𝐏𝐢𝐥𝐢𝐡 𝐟𝐢𝐭𝐮𝐫 𝐲𝐚𝐧𝐠 𝐢𝐧𝐠𝐢𝐧 𝐝𝐢𝐠𝐮𝐧𝐚𝐤𝐚𝐧 ⬇️",
        reply_markup=reply_markup
    )

# ====== MAIN MENU CALLBACK ======
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kembali ke menu utama"""
    query = update.callback_query
    await query.answer()
    await start(update, context)

# ====== REGISTER HANDLERS ======
def register_part1_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(all_menu, pattern="all_menu"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))

# ==================== [ END OF PART 1 ] ====================
# ==================== [ BOT MULTITOOLS - BAGIAN 2 / 3 ] ====================
# ✅ Developer : YinnVPN
# ✅ Revisi : Font teks & tombol, Submenu, Emoji tetap, API key IP Info aktif

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
import requests

# ====== API KEYS ======
IPINFO_API_KEY = "210a01b5fe3d19"

# ============================
# 📌 SUBMENU AD BYPASS
# ============================
async def ad_bypass_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🚀 𝘽𝙖𝙮𝙥𝙖𝙨𝙨 𝙇𝙞𝙣𝙠", callback_data="ad_bypass_process")],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="ad_bypass_info")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🔗 𝐀𝐝 𝐁𝐚𝐲𝐩𝐚𝐬𝐬\n"
        "📌 𝐋𝐚𝐲𝐚𝐧𝐚𝐧 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐦𝐛𝐮𝐤𝐚 𝐥𝐢𝐧𝐤 𝐬𝐡𝐨𝐫𝐭𝐞𝐧 𝐭𝐚𝐧𝐩𝐚 𝐦𝐞𝐧𝐮𝐧𝐠𝐠𝐮.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== PROSES AD BYPASS (SIMULASI / ALTERNATIF TANPA API) ======
async def ad_bypass_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚠️ 𝐊𝐢𝐫𝐢𝐦𝐤𝐚𝐧 𝐥𝐢𝐧𝐤 𝐲𝐚𝐧𝐠 𝐢𝐧𝐠𝐢𝐧 𝐝𝐢𝐛𝐚𝐲𝐩𝐚𝐬𝐬 𝐤𝐞 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭.")

async def ad_bypass_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐀𝐝 𝐁𝐚𝐲𝐩𝐚𝐬𝐬:\n"
        "1️⃣ 𝐊𝐢𝐫𝐢𝐦 𝐥𝐢𝐧𝐤 𝐬𝐡𝐨𝐫𝐭𝐞𝐧 𝐤𝐞 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭.\n"
        "2️⃣ 𝐓𝐮𝐧𝐠𝐠𝐮 𝐛𝐨𝐭 𝐦𝐞𝐦𝐩𝐫𝐨𝐬𝐞𝐬 𝐝𝐚𝐧 𝐦𝐞𝐦𝐛𝐞𝐫𝐢𝐤𝐚𝐧 𝐥𝐢𝐧𝐤 𝐛𝐲𝐩𝐚𝐬𝐬.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="ad_bypass_menu")]])
    )

# ============================
# 📌 SUBMENU IP LOOKUP
# ============================
async def ip_lookup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔍 𝙇𝙤𝙤𝙠𝙪𝙥 𝙄𝙋", callback_data="ip_lookup_process")],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="ip_lookup_info")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    await query.edit_message_text(
        "🌐 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩\n"
        "📌 𝐋𝐚𝐲𝐚𝐧𝐚𝐧 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐧𝐠𝐞𝐜𝐞𝐤 𝐢𝐧𝐟𝐨𝐫𝐦𝐚𝐬𝐢 𝐈𝐏 𝐚𝐝𝐝𝐫𝐞𝐬𝐬.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ip_lookup_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⚠️ 𝐊𝐢𝐫𝐢𝐦𝐤𝐚𝐧 𝐈𝐏 𝐚𝐝𝐝𝐫𝐞𝐬𝐬 𝐲𝐚𝐧𝐠 𝐢𝐧𝐠𝐢𝐧 𝐝𝐢𝐜𝐞𝐤 𝐤𝐞 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭.")

async def ip_lookup_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩:\n"
        "1️⃣ 𝐊𝐢𝐫𝐢𝐦 𝐈𝐏 𝐚𝐝𝐝𝐫𝐞𝐬𝐬 𝐚𝐭𝐚𝐮 𝐝𝐨𝐦𝐚𝐢𝐧 𝐤𝐞 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭.\n"
        "2️⃣ 𝐁𝐨𝐭 𝐚𝐤𝐚𝐧 𝐦𝐞𝐧𝐠𝐠𝐮𝐧𝐚𝐤𝐚𝐧 𝐈𝐏𝐈𝐍𝐅𝐎 𝐀𝐏𝐈 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐧𝐚𝐦𝐩𝐢𝐥𝐤𝐚𝐧 𝐝𝐚𝐭𝐚.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="ip_lookup_menu")]])
    )

# Fungsi untuk memproses IP Lookup
async def process_ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ip_address = update.message.text.strip()
    url = f"https://ipinfo.io/{ip_address}?token={IPINFO_API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        result = (
            f"🌍 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩 𝐑𝐞𝐬𝐮𝐥𝐭\n"
            f"• 𝐈𝐏: {data.get('ip', 'N/A')}\n"
            f"• 𝐎𝐫𝐠: {data.get('org', 'N/A')}\n"
            f"• 𝐋𝐨𝐜𝐚𝐭𝐢𝐨𝐧: {data.get('city', 'N/A')}, {data.get('region', 'N/A')}, {data.get('country', 'N/A')}\n"
            f"• 𝐋𝐚𝐭/𝐋𝐨𝐧: {data.get('loc', 'N/A')}\n"
        )
    except Exception as e:
        result = f"⚠️ 𝐆𝐚𝐠𝐚𝐥 𝐦𝐞𝐧𝐠𝐚𝐦𝐛𝐢𝐥 𝐝𝐚𝐭𝐚: {e}"

    await update.message.reply_text(result)

# ==================== REGISTER HANDLERS PART 2 ====================
def register_part2_handlers(app):
    app.add_handler(CallbackQueryHandler(ad_bypass_menu, pattern="ad_bypass_menu"))
    app.add_handler(CallbackQueryHandler(ad_bypass_process, pattern="ad_bypass_process"))
    app.add_handler(CallbackQueryHandler(ad_bypass_info, pattern="ad_bypass_info"))

    app.add_handler(CallbackQueryHandler(ip_lookup_menu, pattern="ip_lookup_menu"))
    app.add_handler(CallbackQueryHandler(ip_lookup_process, pattern="ip_lookup_process"))
    app.add_handler(CallbackQueryHandler(ip_lookup_info, pattern="ip_lookup_info"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_ip_lookup))

# ==================== [ END OF PART 2 ] ====================
# ==================== BAGIAN 3 - FINAL REVISI ====================
# Lanjutan kode utama bot multi-tools by yinn vpn

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
import asyncio

# ========== 📌 Handler Submenu Admin ==========
async def admin_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("👥 𝘾𝙚𝙠 𝙐𝙨𝙚𝙧 𝙇𝙞𝙨𝙩", callback_data="cek_userlist")],
        [InlineKeyboardButton("📢 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩", callback_data="broadcast_menu")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="main_menu")]
    ]
    msg = await query.message.reply_text("🔧 **𝐀𝐝𝐦𝐢𝐧 𝐌𝐞𝐧𝐮**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    await asyncio.sleep(25)
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg.message_id)

# ========== 📌 Broadcast Menu ==========
async def broadcast_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📝 𝙆𝙞𝙧𝙞𝙢 𝙏𝙚𝙭𝙩", callback_data="broadcast_text")],
        [InlineKeyboardButton("🖼️ 𝙆𝙞𝙧𝙞𝙢 𝙄𝙢𝙖𝙜𝙚", callback_data="broadcast_image")],
        [InlineKeyboardButton("🎭 𝙆𝙞𝙧𝙞𝙢 𝙎𝙩𝙞𝙘𝙠𝙚𝙧", callback_data="broadcast_sticker")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="admin_menu")]
    ]
    await query.message.edit_text("📢 **𝐏𝐢𝐥𝐢𝐡 𝐉𝐞𝐧𝐢𝐬 𝐏𝐞𝐬𝐚𝐧**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ========== 📌 Submenu AdBaypass ==========
async def adbaypass_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔗 𝘽𝙖𝙮𝙥𝙖𝙨 𝙇𝙞𝙣𝙠", callback_data="bypass_link")],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="adbaypass_about")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    await query.message.edit_text("⚡ **𝐀𝐝𝐁𝐚𝐲𝐩𝐚𝐬𝐬 𝐌𝐞𝐧𝐮**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ========== 📌 About AdBaypass ==========
async def adbaypass_about(update, context):
    query = update.callback_query
    await query.answer()
    msg = await query.message.reply_text(
        "📘 **Panduan AdBaypass:**\n"
        "1️⃣ Masukkan link shortener yang ingin di-bypass.\n"
        "2️⃣ Bot akan memproses dan mengirim hasil.\n"
        "3️⃣ Support banyak layanan (Linkvertise, Sub2Get, dll).",
        parse_mode="Markdown"
    )
    await asyncio.sleep(25)
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg.message_id)

# ========== 📌 Handler Submenu SSL Check ==========
async def ssl_menu(update, context):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔍 𝘾𝙚𝙠 𝙎𝙎𝙇", callback_data="check_ssl")],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data="ssl_about")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    await query.message.edit_text("🔐 **𝐒𝐒𝐋 𝐂𝐡𝐞𝐜𝐤 𝐌𝐞𝐧𝐮**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ========== 📌 About SSL Check ==========
async def ssl_about(update, context):
    query = update.callback_query
    await query.answer()
    msg = await query.message.reply_text(
        "📘 **Panduan SSL Check:**\n"
        "1️⃣ Masukkan domain.\n"
        "2️⃣ Bot akan menampilkan info sertifikat SSL.\n"
        "3️⃣ Menunjukkan validitas & masa berlaku.",
        parse_mode="Markdown"
    )
    await asyncio.sleep(25)
    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg.message_id)

# ========== 📌 Handler Callback Registration ==========
def register_part3_handlers(application):
    application.add_handler(CallbackQueryHandler(admin_menu, pattern="admin_menu"))
    application.add_handler(CallbackQueryHandler(broadcast_menu, pattern="broadcast_menu"))
    application.add_handler(CallbackQueryHandler(adbaypass_menu, pattern="adbaypass_menu"))
    application.add_handler(CallbackQueryHandler(adbaypass_about, pattern="adbaypass_about"))
    application.add_handler(CallbackQueryHandler(ssl_menu, pattern="ssl_menu"))
    application.add_handler(CallbackQueryHandler(ssl_about, pattern="ssl_about"))

# ==================== END BAGIAN 3 ====================