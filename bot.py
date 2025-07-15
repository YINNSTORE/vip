import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime

API_TOKEN = '8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE'

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    waiting_for_domain = State()

user_history = {}
scan_results_cache = {}

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🔍 Mulai Scan Subdomain", callback_data="scan"),
        InlineKeyboardButton("📚 Riwayat Pencarian", callback_data="history")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(
        "👋 *Selamat datang di Subdomain Finder Bot!*

"
        "Gunakan tombol di bawah ini untuk mulai mencari subdomain dari domain apa pun.",
        reply_markup=main_menu()
    )

@dp.callback_query_handler(lambda c: c.data == "scan")
async def scan_start(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "📥 Masukkan nama domain (contoh: `example.com`):")
    await Form.waiting_for_domain.set()

@dp.message_handler(state=Form.waiting_for_domain)
async def handle_domain(message: types.Message, state: FSMContext):
    await state.finish()
    domain = message.text.strip().lower()
    loading = await message.answer("🚀 Mencari subdomain...
`[■□□□□□□] Loading...`")

    bars = ["[■□□□□□□]", "[■■□□□□□]", "[■■■□□□□]", "[■■■■□□□]", "[■■■■■□□]", "[■■■■■■□]", "[■■■■■■■]"]
    stop_event = asyncio.Event()

    async def animate():
        i = 0
        while not stop_event.is_set():
            try:
                await loading.edit_text(f"🚀 Mencari subdomain...
`{bars[i % len(bars)]} Loading...`")
                await asyncio.sleep(0.4)
                i += 1
            except: pass

    animation_task = asyncio.create_task(animate())

    try:
        subdomains = await fetch_subdomains(domain)
    except Exception as e:
        logging.error(f"Error: {e}")
        subdomains = []
    finally:
        stop_event.set()
        await animation_task

    if not subdomains:
        await loading.edit_text("❌ Tidak ditemukan subdomain untuk domain tersebut.")
        return

    ip_set = set()
    for sd in subdomains:
        try:
            ip = await resolve_ip(sd["host"])
            if ip:
                sd["ip"] = ip
                ip_set.add(ip)
                sd["asn"], sd["country"] = await get_ip_info(ip)
        except: pass

    on = [s for s in subdomains if is_proxy(s)]
    off = [s for s in subdomains if not is_proxy(s)]
    now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    msg = (
        f"*📄 Hasil Scan:* `{domain}`
"
        f"📅 {now}
"
        f"🔢 Total: {len(subdomains)} | Unik IP: {len(ip_set)}

"
    )
    msg += "🌤️ *Proxy ON:*
" + "
".join([f"• `{s['host']}` ({s.get('ip','-')})" for s in on[:20]]) + ("
..." if len(on)>20 else "")
    msg += "

☁️ *Proxy OFF:*
" + "
".join([f"• `{s['host']}` ({s.get('ip','-')})" for s in off[:20]]) + ("
..." if len(off)>20 else "")

    await loading.edit_text(msg)

    uid = message.from_user.id
    user_history.setdefault(uid, []).append((domain, now))
    scan_results_cache[(uid, domain)] = subdomains

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("⬅️ Kembali", callback_data="back"))
    await message.answer("✅ Scan selesai!", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "history")
async def show_history(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    history = user_history.get(uid, [])
    if not history:
        await bot.send_message(uid, "📭 Belum ada riwayat.", reply_markup=main_menu())
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for domain, tgl in reversed(history[-10:]):
        keyboard.add(InlineKeyboardButton(f"{domain} ({tgl})", callback_data=f"show:{domain}"))
    keyboard.add(InlineKeyboardButton("⬅️ Kembali", callback_data="back"))
    await bot.send_message(uid, "📚 Pilih hasil scan sebelumnya:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("show:"))
async def handle_show(callback_query: types.CallbackQuery):
    uid = callback_query.from_user.id
    domain = callback_query.data.split(":")[1]
    subdomains = scan_results_cache.get((uid, domain), [])
    if not subdomains:
        await bot.send_message(uid, "❌ Data tidak ditemukan.")
        return

    on = [s for s in subdomains if is_proxy(s)]
    off = [s for s in subdomains if not is_proxy(s)]

    msg = (
        f"*📄 Riwayat Scan:* `{domain}`
"
        f"🔢 Total: {len(subdomains)}

"
    )
    msg += "🌤️ *Proxy ON:*
" + "
".join([f"• `{s['host']}`" for s in on[:20]]) + ("
..." if len(on)>20 else "")
    msg += "

☁️ *Proxy OFF:*
" + "
".join([f"• `{s['host']}`" for s in off[:20]]) + ("
..." if len(off)>20 else "")

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("⬅️ Kembali", callback_data="back"))
    await bot.send_message(uid, msg, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == "back")
async def handle_back(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "🏠 Kembali ke menu utama:", reply_markup=main_menu())

async def fetch_subdomains(domain):
    results = set()
    out = []
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(f"https://api.hackertarget.com/hostsearch/?q={domain}") as r:
                text = await r.text()
                for line in text.strip().splitlines():
                    if "," in line:
                        sub, _ = line.split(",", 1)
                        results.add(sub.strip())
        except: pass

        try:
            async with session.get(f"https://dns.bufferover.run/dns?q=.{domain}") as r:
                json_data = await r.json()
                records = json_data.get("FDNS_A", [])
                for rec in records:
                    part = rec.split(",")[-1]
                    if domain in part:
                        results.add(part.strip())
        except: pass

    for host in sorted(results):
        out.append({"host": host})
    return out

async def resolve_ip(host):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://dns.google/resolve?name={host}&type=A") as r:
                json_data = await r.json()
                answer = json_data.get("Answer", [])
                for a in answer:
                    if a.get("type") == 1:
                        return a["data"]
    except: return None

async def get_ip_info(ip):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://ip-api.com/json/{ip}?fields=as,country") as r:
                data = await r.json()
                return data.get("as", "N/A"), data.get("country", "Unknown")
    except:
        return "N/A", "Unknown"

def is_proxy(sd):
    keywords = ["cdn", "cloud", "akamai", "edge", "cache"]
    return any(k in sd["host"] for k in keywords)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
