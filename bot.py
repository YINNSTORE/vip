import logging
import asyncio
import aiohttp
import io
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_history = {}

class Form(StatesGroup):
    waiting_for_domain = State()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔍 Mulai Cari Subdomain", callback_data='search'),
        InlineKeyboardButton("📚 Riwayat Pencarian", callback_data='history')
    )
    banner = (
        "🌐 *Selamat datang di Bot Subdomain Finder!*\n\n"
        "🔎 Bot ini membantu kamu mencari subdomain tersembunyi dari domain publik.\n\n"
        "⚙️ *Fitur:*\n"
        "• Gabungan dari 3 sumber tanpa API\n"
        "• Urutan hasil berdasarkan proxy\n"
        "• Ekspor hasil ke file\n"
        "• Riwayat pencarian\n\n"
        "Silakan pilih menu di bawah ini untuk mulai."
    )
    await message.answer(banner, parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query_handler(Text(equals='search'))
async def handle_search(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "📥 Masukkan nama domain (contoh: `example.com`):", parse_mode="Markdown")
    await Form.waiting_for_domain.set()

@dp.message_handler(state=Form.waiting_for_domain)
async def process_domain(message: types.Message, state: FSMContext):
    domain = message.text.strip().lower()
    await state.finish()

    loading_msg = await message.answer("🚀 Mencari subdomain...\n`[■□□□□□□] Loading...`", parse_mode="Markdown")

    loading_bars = ["[■□□□□□□]", "[■■□□□□□]", "[■■■□□□□]", "[■■■■□□□]", "[■■■■■□□]", "[■■■■■■□]", "[■■■■■■■]"]
    loading_done = asyncio.Event()

    async def animate_loading():
        i = 0
        while not loading_done.is_set():
            bar = loading_bars[i % len(loading_bars)]
            try:
                await loading_msg.edit_text(f"🚀 Mencari subdomain...\n`{bar} Loading...`", parse_mode="Markdown")
            except:
                pass
            await asyncio.sleep(0.4)
            i += 1

    loading_task = asyncio.create_task(animate_loading())

    try:
        subs = await find_subdomains_all(domain)
    except Exception as e:
        loading_done.set()
        await loading_task
        await loading_msg.edit_text(f"❌ Terjadi kesalahan saat mencari:\n`{e}`", parse_mode="Markdown")
        return

    loading_done.set()
    await loading_task

    if not subs:
        await loading_msg.edit_text(f"❗ Tidak ditemukan subdomain untuk `{domain}`.", parse_mode="Markdown")
        return

    sorted_subs = sorted(set(subs), key=lambda x: not ("cdn" in x or "cloudflare" in x))

    text_result = f"✅ *Subdomain ditemukan untuk:* `{domain}`\n\n"
    for s in sorted_subs:
        status = "🟢 Proxy ON" if ("cdn" in s or "cloudflare" in s) else "🔴 Proxy OFF"
        text_result += f"• `{s}` - {status}\n"

    count_on = sum(1 for s in sorted_subs if "cdn" in s or "cloudflare" in s)
    count_off = len(sorted_subs) - count_on
    text_result += f"\n📊 Total: {len(sorted_subs)} | 🟢 ON: {count_on} | 🔴 OFF: {count_off}"

    await loading_msg.edit_text(text_result, parse_mode="Markdown")

    file_content = "\n".join(sorted_subs)
    file = io.StringIO(file_content)
    file.name = f"{domain}_subdomains.txt"
    await bot.send_document(message.chat.id, InputFile(file))

    uid = message.from_user.id
    user_history.setdefault(uid, []).append((domain, sorted_subs))

@dp.callback_query_handler(Text(equals='history'))
async def handle_history(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    uid = callback_query.from_user.id
    history = user_history.get(uid, [])
    if not history:
        await bot.send_message(uid, "📭 Belum ada riwayat pencarian.")
        return

    msg = "📚 *Riwayat Terakhir:*\n\n"
    for i, (domain, subs) in enumerate(history[-5:], 1):
        msg += f"{i}. `{domain}` ({len(subs)} subdomain)\n"
    await bot.send_message(uid, msg, parse_mode="Markdown")

# Fungsi gabungan dari crt.sh, rapiddns.io, dan hackertarget
async def find_subdomains_all(domain):
    results = set()
    timeout = aiohttp.ClientTimeout(total=10)

    # crt.sh
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as r:
                if r.status == 200:
                    json_data = await r.json(content_type=None)
                    for entry in json_data:
                        name = entry.get("name_value", "")
                        for item in name.split("\n"):
                            if "*" not in item:
                                results.add(item.strip())
    except Exception as e:
        logging.warning(f"crt.sh error: {e}")

    # rapiddns.io
    try:
        url = f"https://rapiddns.io/subdomain/{domain}?full=1"
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as r:
                if r.status == 200:
                    html = await r.text()
                    import re
                    matches = re.findall(r'<td>([a-zA-Z0-9_.-]+\.' + re.escape(domain) + r')</td>', html)
                    results.update(matches)
    except Exception as e:
        logging.warning(f"rapiddns error: {e}")

    # hackertarget
    try:
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as r:
                if r.status == 200:
                    txt = await r.text()
                    for line in txt.splitlines():
                        if "," in line:
                            sub, _ = line.split(",")
                            results.add(sub.strip())
    except Exception as e:
        logging.warning(f"hackertarget error: {e}")

    return list(results)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
