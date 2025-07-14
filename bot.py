import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime
import re

API_TOKEN = '8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_history = {}

class Form(StatesGroup):
    waiting_for_domain = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🔍 Mulai Scan Subdomain", callback_data="scan"))
    keyboard.add(InlineKeyboardButton("📚 Riwayat Pencarian", callback_data="history"))
    banner = (
        "🌐 *Selamat datang di Bot Subdomain Finder!*\n\n"
        "🔎 Bot ini membantu kamu mencari subdomain tersembunyi dari domain publik.\n\n"
        "⚙️ *Fitur:*\n"
        "• Gabungan dari 3 sumber tanpa API\n"
        "• Pisahkan hasil berdasarkan Proxy ON/OFF\n"
        "• Tampilkan IP unik, jumlah subdomain\n"
        "• Interaktif via tombol\n\n"
        "Silakan pilih menu di bawah."
    )
    await message.answer(banner, parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query_handler(Text(equals="scan"))
async def scan_start(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "📥 Masukkan nama domain (contoh: `example.com`):", parse_mode="Markdown")
    await Form.waiting_for_domain.set()

@dp.message_handler(state=Form.waiting_for_domain)
async def handle_domain_input(message: types.Message, state: FSMContext):
    await state.finish()
    domain = message.text.strip().lower()

    loading = await message.answer("🚀 Mencari subdomain...\n`[■□□□□□□] Loading...`", parse_mode="Markdown")
    bars = ["[■□□□□□□]", "[■■□□□□□]", "[■■■□□□□]", "[■■■■□□□]", "[■■■■■□□]", "[■■■■■■□]", "[■■■■■■■]"]
    stop_event = asyncio.Event()

    async def animate():
        i = 0
        while not stop_event.is_set():
            bar = bars[i % len(bars)]
            try:
                await loading.edit_text(f"🚀 Mencari subdomain...\n`{bar} Loading...`", parse_mode="Markdown")
            except: pass
            await asyncio.sleep(0.5)
            i += 1

    animation_task = asyncio.create_task(animate())

    try:
        results = await find_subdomains(domain)
    except Exception as e:
        results = []
        logging.error(f"Error: {e}")
    finally:
        stop_event.set()
        await animation_task

    if not results:
        await loading.edit_text("❌ Tidak ditemukan subdomain.")
        return

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(results)
    unique_ips = len(set(ip for _, ip in results))

    proxy_on = [(sub, ip) for sub, ip in results if is_proxy_ip(ip)]
    proxy_off = [(sub, ip) for sub, ip in results if not is_proxy_ip(ip)]

    response = f"📝 *Hasil Scan:* `{domain}`\n"
    response += f"📅 Tanggal: {now}\n"
    response += f"🔢 Subdomain: {total} | 📡 IP Unik: {unique_ips}\n\n"

    response += "☁️ *Proxy ON:*\n"
    for sub, ip in proxy_on:
        response += f"• `{sub}` – `{ip}`\n"
    response += "\n🚫 *Proxy OFF:*\n"
    for sub, ip in proxy_off:
        response += f"• `{sub}` – `{ip}`\n"

    await loading.edit_text(response, parse_mode="Markdown")

    user_history.setdefault(message.from_user.id, []).append((domain, now, total))

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔁 Scan Ulang", callback_data=f"rescan:{domain}"))
    await message.answer("Ingin melakukan tindakan lain?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("rescan:"))
async def handle_rescan(callback_query: types.CallbackQuery):
    domain = callback_query.data.split(":")[1]
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"📥 Ulangi scan untuk: `{domain}`", parse_mode="Markdown")
    await Form.waiting_for_domain.set()

@dp.callback_query_handler(Text(equals="history"))
async def show_history(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    history = user_history.get(uid, [])
    if not history:
        await bot.send_message(uid, "📭 Belum ada riwayat.")
        return

    msg = "📚 *Riwayat Pencarian Kamu:*\n\n"
    for i, (domain, date, total) in enumerate(history[-5:], 1):
        msg += f"{i}. `{domain}` – {total} subdomain ({date})\n"
    await bot.send_message(uid, msg, parse_mode="Markdown")

async def find_subdomains(domain):
    timeout = aiohttp.ClientTimeout(total=15)
    found = set()

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(f"https://crt.sh/?q=%25.{domain}&output=json") as r:
                data = await r.json(content_type=None)
                for item in data:
                    names = item.get("name_value", "").split("\n")
                    for name in names:
                        if "*" not in name:
                            found.add(name.strip())
        except: pass

        try:
            async with session.get(f"https://rapiddns.io/subdomain/{domain}?full=1") as r:
                html = await r.text()
                matches = re.findall(r'<td>([a-zA-Z0-9_.-]+\.' + re.escape(domain) + r')</td>', html)
                for m in matches:
                    found.add(m.strip())
        except: pass

        try:
            async with session.get(f"https://api.hackertarget.com/hostsearch/?q={domain}") as r:
                txt = await r.text()
                for line in txt.splitlines():
                    if "," in line:
                        sub, _ = line.split(",")
                        found.add(sub.strip())
        except: pass

        result = []
        for sub in sorted(found):
            try:
                ip = (await session.get(f"https://dns.google/resolve?name={sub}&type=A")).json()
                data = await ip
                ip_addr = data.get("Answer", [{}])[0].get("data", "-")
            except:
                ip_addr = "-"
            result.append((sub, ip_addr))

    return result

def is_proxy_ip(ip):
    return ip.startswith("34.") or ip.startswith("104.") or ip.startswith("35.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
