import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests

# ==========================
# 🔹 Konfigurasi BOT
# ==========================
TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"
ADMIN_ID = 6353421952
IPINFO_API_KEY = "210a01b5fe3d19"  # ← API IP Lookup sudah diisi

# ==========================
# 🔹 Logging
# ==========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==========================
# 🔹 Menu Utama
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌐 𝙄𝙋 𝙇𝙤𝙤𝙠𝙪𝙥", callback_data='ip_lookup_menu')],
        [InlineKeyboardButton("🛡️ 𝙋𝙧𝙤𝙭𝙮 𝘾𝙝𝙚𝙘𝙠𝙚𝙧", callback_data='proxy_checker_menu')],
        [InlineKeyboardButton("🔗 𝘼𝙙 𝘽𝙮𝙥𝙖𝙨𝙨", callback_data='adbypass_menu')],
        [InlineKeyboardButton("🌍 𝙎𝙪𝙗𝙙𝙤𝙢𝙖𝙞𝙣 𝙁𝙞𝙣𝙙𝙚𝙧", callback_data='subdomain_finder_menu')],
        [InlineKeyboardButton("👑 𝘼𝙙𝙢𝙞𝙣", callback_data='admin_menu')],
        [InlineKeyboardButton("📞 𝘾𝙤𝙣𝙩𝙖𝙘𝙩", url="https://t.me/yinnprovpn")]
    ]
    await update.message.reply_text(
        "🤖 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐌𝐲 𝐓𝐨𝐨𝐥𝐬 𝐁𝐨𝐭\n\nSilahkan pilih menu di bawah ⬇️",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================
# 🔹 Submenu IP Lookup
# ==========================
async def ip_lookup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔎 𝘾𝙚𝙠 𝙄𝙋", callback_data='ip_lookup')],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data='ip_lookup_guide')],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='main_menu')]
    ]
    await query.edit_message_text("🌐 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩 𝐌𝐞𝐧𝐮", reply_markup=InlineKeyboardMarkup(keyboard))

async def ip_lookup_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐈𝐏 𝐋𝐨𝐨𝐤𝐮𝐩:\n\n"
        "1️⃣ Klik 'Cek IP'\n"
        "2️⃣ Masukkan IP target\n"
        "3️⃣ Bot akan menampilkan detail lokasi, ISP, dan lainnya.\n\n"
        "Gunakan fitur ini dengan bijak ✅",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='ip_lookup_menu')]])
    )

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔎 𝐊𝐢𝐫𝐢𝐦 𝐈𝐏 𝐚𝐝𝐝𝐫𝐞𝐬𝐬 𝐲𝐚𝐧𝐠 𝐢𝐧𝐠𝐢𝐧 𝐝𝐢 𝐥𝐢𝐡𝐚𝐭:")

    context.user_data["awaiting_ip"] = True

async def handle_ip_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_ip"):
        ip = update.message.text
        url = f"https://ipinfo.io/{ip}?token={IPINFO_API_KEY}"
        try:
            data = requests.get(url).json()
            hasil = (
                f"🌐 **𝐈𝐏 𝐈𝐧𝐟𝐨:**\n"
                f"📍 Lokasi: {data.get('city')}, {data.get('region')}, {data.get('country')}\n"
                f"🏢 ISP: {data.get('org')}\n"
                f"🌎 Koordinat: {data.get('loc')}\n"
            )
            await update.message.reply_text(hasil)
        except:
            await update.message.reply_text("❌ Gagal mengambil data IP.")
        context.user_data["awaiting_ip"] = False

# ==========================
# 🔹 Submenu Admin
# ==========================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📢 𝘽𝙧𝙤𝙖𝙙𝙘𝙖𝙨𝙩", callback_data='broadcast')],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data='admin_guide')],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='main_menu')]
    ]
    await query.edit_message_text("👑 𝐀𝐝𝐦𝐢𝐧 𝐌𝐞𝐧𝐮", reply_markup=InlineKeyboardMarkup(keyboard))

# ==========================
# 🔹 Submenu Proxy Checker
# ==========================
async def proxy_checker_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔍 𝘾𝙚𝙠 𝙋𝙧𝙤𝙭𝙮", callback_data='proxy_checker')],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data='proxy_guide')],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='main_menu')]
    ]
    await query.edit_message_text("🛡️ 𝐌𝐞𝐧𝐮 𝐏𝐫𝐨𝐱𝐲 𝐂𝐡𝐞𝐜𝐤𝐞𝐫", reply_markup=InlineKeyboardMarkup(keyboard))

async def proxy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐏𝐫𝐨𝐱𝐲 𝐂𝐡𝐞𝐜𝐤𝐞𝐫:\n\n"
        "1️⃣ Klik 'Cek Proxy'\n"
        "2️⃣ Masukkan IP dan Port\n"
        "3️⃣ Bot akan mendeteksi apakah proxy aktif atau tidak ✅",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='proxy_checker_menu')]])
    )

# ==========================
# 🔹 Submenu Ad Bypass
# ==========================
async def adbypass_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔗 𝘽𝙮𝙥𝙖𝙨𝙨 𝙇𝙞𝙣𝙠", callback_data='adbypass')],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data='adbypass_guide')],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='main_menu')]
    ]
    await query.edit_message_text("🔗 𝐀𝐝 𝐁𝐲𝐩𝐚𝐬𝐬 𝐌𝐞𝐧𝐮", reply_markup=InlineKeyboardMarkup(keyboard))

async def adbypass_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐀𝐝 𝐁𝐲𝐩𝐚𝐬𝐬:\n\n"
        "1️⃣ Klik 'Bypass Link'\n"
        "2️⃣ Masukkan link yang ingin dibuka\n"
        "3️⃣ Bot akan mencoba melewati halaman iklan otomatis ✅",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='adbypass_menu')]])
    )

# ==========================
# 🔹 Submenu Subdomain Finder
# ==========================
async def subdomain_finder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌍 𝘾𝙖𝙧𝙞 𝙎𝙪𝙗𝙙𝙤𝙢𝙖𝙞𝙣", callback_data='subdomain_finder')],
        [InlineKeyboardButton("📖 𝙋𝙖𝙣𝙙𝙪𝙖𝙣", callback_data='subdomain_guide')],
        [InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='main_menu')]
    ]
    await query.edit_message_text("🌍 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧 𝐅𝐢𝐧𝐝𝐞𝐫 𝐌𝐞𝐧𝐮", reply_markup=InlineKeyboardMarkup(keyboard))

async def subdomain_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 𝐏𝐚𝐧𝐝𝐮𝐚𝐧 𝐒𝐮𝐛𝐝𝐨𝐦𝐚𝐢𝐧 𝐅𝐢𝐧𝐝𝐞𝐫:\n\n"
        "1️⃣ Klik 'Cari Subdomain'\n"
        "2️⃣ Masukkan domain target (contoh: site.com)\n"
        "3️⃣ Bot akan menampilkan daftar subdomain yang ditemukan ✅",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ 𝙆𝙚𝙢𝙗𝙖𝙡𝙞", callback_data='subdomain_finder_menu')]])
    )

# ==========================
# 🔹 Callback untuk Main Menu
# ==========================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await start(update, context)

# ==========================
# 🔹 Handler & Main Function
# ==========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ip_lookup_menu, pattern='ip_lookup_menu'))
    app.add_handler(CallbackQueryHandler(ip_lookup, pattern='ip_lookup'))
    app.add_handler(CallbackQueryHandler(ip_lookup_guide, pattern='ip_lookup_guide'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ip_input))

    app.add_handler(CallbackQueryHandler(proxy_checker_menu, pattern='proxy_checker_menu'))
    app.add_handler(CallbackQueryHandler(proxy_guide, pattern='proxy_guide'))

    app.add_handler(CallbackQueryHandler(adbypass_menu, pattern='adbypass_menu'))
    app.add_handler(CallbackQueryHandler(adbypass_guide, pattern='adbypass_guide'))

    app.add_handler(CallbackQueryHandler(subdomain_finder_menu, pattern='subdomain_finder_menu'))
    app.add_handler(CallbackQueryHandler(subdomain_guide, pattern='subdomain_guide'))

    app.add_handler(CallbackQueryHandler(admin_menu, pattern='admin_menu'))
    app.add_handler(CallbackQueryHandler(main_menu, pattern='main_menu'))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()