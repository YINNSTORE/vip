import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# --- Konfigurasi Awal ---
TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"
ADMIN_ID = 6353421952

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📂 𝘼𝙡𝙡 𝙈𝙚𝙣𝙪", callback_data="all_menu")],
        [InlineKeyboardButton("👤 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝘼𝙙𝙢𝙞𝙣", url="https://t.me/yinnprovpn")],
        [InlineKeyboardButton("🛠️ 𝘼𝙙𝙢𝙞𝙣 𝙈𝙚𝙣𝙪", callback_data="admin_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 𝐒𝐞𝐥𝐚𝐦𝐚𝐭 𝐝𝐚𝐭𝐚𝐧𝐠 𝐝𝐢 𝐛𝐨𝐭 𝐦𝐮𝐥𝐭𝐢𝐭𝐨𝐨𝐥𝐬 𝐛𝐲 𝐲𝐢𝐧𝐧 𝐯𝐩𝐧!\n"
        "🔹 Gunakan bot ini dengan bijak.\n\n"
        "📌 Tekan tombol di bawah untuk mulai.",
        reply_markup=reply_markup
    )

# --- Menu Utama ---
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔗 𝘼𝙙 𝘽𝙮𝙥𝙖𝙨𝙨", callback_data="ad_bypass")],
        [InlineKeyboardButton("🌐 𝙋𝙧𝙤𝙭𝙮 𝘾𝙝𝙚𝙘𝙠𝙚𝙧", callback_data="proxy_checker")],
        [InlineKeyboardButton("🔍 𝙄𝙋 𝙇𝙤𝙤𝙠𝙪𝙥", callback_data="ip_lookup")],
        [InlineKeyboardButton("📡 𝙎𝙐𝘽𝘿𝙊𝙈𝘼𝙄𝙉 𝙁𝙞𝙣𝙙𝙚𝙧", callback_data="subdomain_finder")],
        [InlineKeyboardButton("🔐 𝙎𝙎𝙇 𝘾𝙝𝙚𝙘𝙠𝙚𝙧", callback_data="ssl_checker")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞 𝙆𝙚 𝙈𝙚𝙣𝙪 𝙐𝙩𝙖𝙢𝙖", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="📂 𝐒𝐞𝐦𝐮𝐚 𝐌𝐞𝐧𝐮 𝐅𝐢𝐭𝐮𝐫:\n"
             "Pilih salah satu fitur di bawah untuk menggunakan tool.",
        reply_markup=reply_markup
    )

# --- Menu Admin ---
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📋 𝘾𝙚𝙠 𝙐𝙨𝙚𝙧 𝙇𝙞𝙨𝙩", callback_data="user_list")],
        [InlineKeyboardButton("📢 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩", callback_data="broadcast")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞 𝙆𝙚 𝙈𝙚𝙣𝙪 𝙐𝙩𝙖𝙢𝙖", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🛠️ 𝐌𝐞𝐧𝐮 𝐀𝐝𝐦𝐢𝐧\n\n"
             "Pilih aksi yang ingin dilakukan:",
        reply_markup=reply_markup
    )

# --- Submenu Ad Bypass ---
async def ad_bypass_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📌 𝙆𝙞𝙧𝙞𝙢 𝙇𝙞𝙣𝙠 𝙐𝙣𝙩𝙪𝙠 𝘽𝙮𝙥𝙖𝙨𝙨", callback_data="ad_bypass_process")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣 𝘼𝙙 𝘽𝙮𝙥𝙖𝙨𝙨", callback_data="ad_bypass_guide")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🔗 𝐀𝐝 𝐁𝐲𝐩𝐚𝐬𝐬\n\n"
             "Kirimkan link yang ingin kamu bypass menggunakan fitur ini.",
        reply_markup=reply_markup
    )

# --- Submenu Proxy Checker ---
async def proxy_checker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📌 𝙆𝙞𝙧𝙞𝙢 𝙄𝙋 𝙋𝙧𝙤𝙭𝙮 𝙐𝙣𝙩𝙪𝙠 𝘾𝙚𝙠", callback_data="proxy_checker_process")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣 𝙋𝙧𝙤𝙭𝙮 𝘾𝙝𝙚𝙘𝙠𝙚𝙧", callback_data="proxy_checker_guide")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🌐 𝐏𝐫𝐨𝐱𝐲 𝐂𝐡𝐞𝐜𝐤𝐞𝐫\n\n"
             "Masukkan IP atau daftar proxy untuk dicek validitasnya.",
        reply_markup=reply_markup
    )

# --- Submenu IP Lookup ---
async def ip_lookup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📌 𝙆𝙞𝙧𝙞𝙢 𝙄𝙋 / 𝙇𝙞𝙣𝙠 𝙐𝙣𝙩𝙪𝙠 𝙇𝙤𝙤𝙠𝙪𝙥", callback_data="ip_lookup_process")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣 𝙄𝙋 𝙇𝙤𝙤𝙠𝙪𝙥", callback_data="ip_lookup_guide")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🔍 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩\n\n"
             "Kirimkan IP atau domain untuk mendapatkan detail informasinya.",
        reply_markup=reply_markup
    )

# --- Submenu Subdomain Finder ---
async def subdomain_finder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📌 𝙆𝙞𝙧𝙞𝙢 𝘿𝙤𝙢𝙖𝙞𝙣 𝙐𝙣𝙩𝙪𝙠 𝙎𝙘𝙖𝙣", callback_data="subdomain_finder_process")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣 𝙎𝙪𝙗𝙙𝙤𝙢𝙖𝙞𝙣 𝙁𝙞𝙣𝙙𝙚𝙧", callback_data="subdomain_finder_guide")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="📡 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧 𝐅𝐢𝐧𝐝𝐞𝐫\n\n"
             "Masukkan domain utama untuk menemukan subdomain yang aktif.",
        reply_markup=reply_markup
    )

# --- Submenu SSL Checker ---
async def ssl_checker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📌 𝙆𝙞𝙧𝙞𝙢 𝙇𝙞𝙣𝙠 𝙐𝙣𝙩𝙪𝙠 𝘾𝙚𝙠", callback_data="ssl_checker_process")],
        [InlineKeyboardButton("ℹ️ 𝙋𝙖𝙣𝙙𝙪𝙖𝙣 𝙎𝙎𝙇 𝘾𝙝𝙚𝙘𝙠𝙚𝙧", callback_data="ssl_checker_guide")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="all_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="🔐 𝐒𝐒𝐋 𝐂𝐡𝐞𝐜𝐤𝐞𝐫\n\n"
             "Kirimkan link website untuk memeriksa status SSL Certificate.",
        reply_markup=reply_markup
    )

# --- Submenu Admin ---
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📢 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩", callback_data="broadcast")],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="👑 𝐌𝐞𝐧𝐮 𝐀𝐝𝐦𝐢𝐧\n\n"
             "Gunakan fitur ini untuk mengirim pesan ke semua pengguna bot.",
        reply_markup=reply_markup
    )

# --- Panduan untuk setiap fitur ---
async def ad_bypass_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐀𝐝 𝐁𝐲𝐩𝐚𝐬𝐬\n\n"
             "1️⃣ Klik *Kirim Link* di menu sebelumnya.\n"
             "2️⃣ Kirimkan link iklan yang ingin dibypass.\n"
             "3️⃣ Tunggu bot memberikan hasil link asli tanpa iklan.\n\n"
             "⚠️ Tidak semua link didukung 100%.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="ad_bypass_menu")]])
    )

async def proxy_checker_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐏𝐫𝐨𝐱𝐲 𝐂𝐡𝐞𝐜𝐤𝐞𝐫\n\n"
             "1️⃣ Klik *Kirim IP Proxy* di menu sebelumnya.\n"
             "2️⃣ Masukkan daftar proxy atau satu proxy.\n"
             "3️⃣ Bot akan mengecek apakah proxy valid atau tidak.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="proxy_checker_menu")]])
    )

async def ip_lookup_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩\n\n"
             "1️⃣ Klik *Kirim IP/Link* di menu sebelumnya.\n"
             "2️⃣ Kirimkan IP address atau domain.\n"
             "3️⃣ Bot akan memberikan informasi detail tentang IP tersebut.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="ip_lookup_menu")]])
    )

async def subdomain_finder_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧 𝐅𝐢𝐧𝐝𝐞𝐫\n\n"
             "1️⃣ Klik *Kirim Domain* di menu sebelumnya.\n"
             "2️⃣ Masukkan domain utama (contoh: example.com).\n"
             "3️⃣ Bot akan mencari subdomain aktif yang terdeteksi.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="subdomain_finder_menu")]])
    )

async def ssl_checker_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐒𝐒𝐋 𝐂𝐡𝐞𝐜𝐤𝐞𝐫\n\n"
             "1️⃣ Klik *Kirim Link* di menu sebelumnya.\n"
             "2️⃣ Masukkan URL website.\n"
             "3️⃣ Bot akan menampilkan informasi sertifikat SSL situs tersebut.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data="ssl_checker_menu")]])
    )