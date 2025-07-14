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
    await message.answer("👋 *Selamat datang di Subdomain Finder Bot berbasis API!*\n\n🔎 Gunakan tombol di bawah ini untuk mulai mencari subdomain dari domain apa pun!", parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query_handler(Text(equals="scan"))
async def scan_start(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "📥 Masukkan nama domain (contoh: `example.com`):", parse_mode="Markdown")
    await Form.waiting_for_domain.set()

@dp.message_handler(state=Form.waiting_for_domain)
async def handle_domain(message: types.Message, state: FSMContext):
    await state.finish()
    domain = message.text.strip().lower()

    loading = await message.answer("🚀 Mencari subdomain...\n`[■□□□□□□] Loading...`", parse_mode="Markdown")
    bars = ["[■□□□□□□]", "[■■□□□□□]", "[■■■□□□□]", "[■■■■□□□]", "[■■■■■□□]", "[■■■■■■□]", "[■■■■■■■]"]
    stop_event = asyncio.Event()

    async def animate():
        i = 0
        while not stop_event.is_set():
            try:
                bar = bars[i % len(bars)]
                await loading.edit_text(f"🚀 Mencari subdomain...\n`{bar} Loading...`", parse_mode="Markdown")
                await asyncio.sleep(0.4)
                i += 1
            except:
                pass

    animation_task = asyncio.create_task(animate())
    try:
        subdomains = await fetch_subdomains(domain)
    except Exception as e:
        logging.error(f"Gagal fetch: {e}")
        subdomains = []
    finally:
        stop_event.set()
        await animation_task

    if not subdomains:
        await loading.edit_text("❌ Tidak ditemukan subdomain untuk domain tersebut.")
        return

    on = [s for s in subdomains if is_proxy(s)]
    off = [s for s in subdomains if not is_proxy(s)]
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"📝 *Hasil Scan:* `{domain}`\n📅 Tanggal: {now}\n🔢 Total: {len(subdomains)}\n\n"
    msg += "☁️ *Proxy ON:*\n" + "\n".join(f"• `{s}`" for s in on[:15]) + ("\n..." if len(on) > 15 else "")
    msg += "\n\n🚫 *Proxy OFF:*\n" + "\n".join(f"• `{s}`" for s in off[:15]) + ("\n..." if len(off) > 15 else "")

    await loading.edit_text(msg, parse_mode="Markdown")
    user_history.setdefault(message.from_user.id, []).append((domain, now, len(subdomains)))

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

    msg = "📚 *Riwayat Terakhir:*\n\n"
    for i, (domain, tgl, total) in enumerate(history[-5:], 1):
        msg += f"{i}. `{domain}` – {total} subdomain ({tgl})\n"
    await bot.send_message(uid, msg, parse_mode="Markdown")

async def fetch_subdomains(domain):
    results = set()
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(f"https://api.hackertarget.com/hostsearch/?q={domain}") as r:
                text = await r.text()
                for line in text.strip().splitlines():
                    if "," in line:
                        sub, _ = line.split(",")
                        results.add(sub.strip())
        except Exception as e:
            logging.warning(f"Hackertarget error: {e}")

        try:
            async with session.get(f"https://dns.bufferover.run/dns?q=.\{domain}") as r:
                json_data = await r.json()
                records = json_data.get("FDNS_A", [])
                for rec in records:
                    part = rec.split(",")[-1]
                    if domain in part:
                        results.add(part.strip())
        except Exception as e:
            logging.warning(f"Bufferover error: {e}")

    return list(results)

def is_proxy(sub):
    # Naif check untuk demo, bisa ditambah pengecekan IP ASN cloudflare/CDN
    return any(key in sub for key in ["cdn", "cloud", "cache", "images", "static"])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
