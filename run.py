import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Simpan riwayat pengguna
user_history = {}

# State machine
class Form(StatesGroup):
    waiting_for_domain = State()

# /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔎 Mulai Pencarian", callback_data='search'),
        InlineKeyboardButton("🗂️ Lihat Riwayat", callback_data='history')
    )

    banner = (
        "🌐 *Selamat datang di Subdomain Explorer Bot!*\n\n"
        "🧠 Bot ini dirancang untuk membantu kamu menemukan subdomain tersembunyi dari sebuah domain utama. "
        "Gunakan tools ini untuk keperluan OSINT, analisis keamanan, atau hanya sekadar eksplorasi teknis.\n\n"
        "⚙️ *Fitur Unggulan:*\n"
        "• Pencarian subdomain otomatis & cepat\n"
        "• Urutan berdasarkan status proxy\n"
        "• Riwayat pencarian pribadi\n\n"
        "🔽 Silakan pilih menu di bawah untuk memulai:"
    )
    await message.answer(banner, parse_mode="Markdown", reply_markup=keyboard)

# Ketika tombol Mulai Pencarian ditekan
@dp.callback_query_handler(Text(equals='search'))
async def handle_search(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "🔍 Masukkan nama domain (contoh: `example.com`):", parse_mode="Markdown")
    await Form.waiting_for_domain.set()

# Handle input domain
@dp.message_handler(state=Form.waiting_for_domain)
async def process_domain(message: types.Message, state: FSMContext):
    domain = message.text.strip()
    await state.finish()

    loading_msg = await message.answer("🚀 Mencari subdomain...\n`[■■■□□□□] Loading...`", parse_mode="Markdown")

    # Simulasi animasi loading
    for bar in ["[■■■□□□□]", "[■■■■■□□]", "[■■■■■■■]"]:
        await loading_msg.edit_text(f"🚀 Mencari subdomain...\n`{bar} Loading...`", parse_mode="Markdown")
        await asyncio.sleep(0.5)

    # Ambil subdomain (dummy)
    subdomains = await find_subdomains(domain)

    # Urutkan: proxy on (True) dulu
    sorted_subs = sorted(subdomains, key=lambda x: not x['proxy'])

    text_result = f"✅ *Subdomain ditemukan untuk:* `{domain}`\n\n"
    for sub in sorted_subs:
        status = "🟢 Proxy ON" if sub["proxy"] else "🔴 Proxy OFF"
        text_result += f"• `{sub['host']}` - {status}\n"

    await loading_msg.edit_text(text_result, parse_mode="Markdown")

    # Simpan history user
    uid = message.from_user.id
    user_history.setdefault(uid, []).append((domain, sorted_subs))

# Ketika tombol Lihat Riwayat ditekan
@dp.callback_query_handler(Text(equals='history'))
async def handle_history(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    uid = callback_query.from_user.id

    history = user_history.get(uid, [])
    if not history:
        await bot.send_message(uid, "❌ Belum ada riwayat pencarian.")
        return

    message = "📜 *Riwayat Pencarian Terakhir:*\n\n"
    for i, (domain, subs) in enumerate(history[-5:], 1):
        message += f"{i}. `{domain}` ({len(subs)} subdomain ditemukan)\n"

    await bot.send_message(uid, message, parse_mode="Markdown")

# Dummy subdomain finder (ganti dengan API asli jika perlu)
async def find_subdomains(domain):
    return [
        {"host": f"api.{domain}", "proxy": True},
        {"host": f"dev.{domain}", "proxy": False},
        {"host": f"cdn.{domain}", "proxy": True},
        {"host": f"mail.{domain}", "proxy": False}
    ]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
