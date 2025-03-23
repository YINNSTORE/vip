import os
import openai
import asyncio
import logging
import fitz  # Baca PDF
import requests
import pytz
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from pydub import AudioSegment

# **🔹 API Key**
BOT_TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"
OPENAI_API_KEY = ""

# **🔹 ID Admin Awal**
ADMIN_IDS = {6353421952}  # Ganti dengan ID Admin pertama (Owner)

# Inisialisasi bot & OpenAI
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

# **🔹 Keyboard Menu**
menu = InlineKeyboardMarkup()
menu.add(InlineKeyboardButton("💬 Chat AI", callback_data="chat_ai"))
menu.add(InlineKeyboardButton("☁️ Cek Cuaca", callback_data="cek_cuaca"))
menu.add(InlineKeyboardButton("🧮 Kalkulator", callback_data="kalkulator"))
menu.add(InlineKeyboardButton("🌎 Translate", callback_data="translate"))
menu.add(InlineKeyboardButton("📖 Quotes", callback_data="quotes"))
menu.add(InlineKeyboardButton("🕒 Waktu Dunia", callback_data="waktu_dunia"))
menu.add(InlineKeyboardButton("📰 Berita Terbaru", callback_data="berita"))

# **🔹 Keyboard Premium (Hanya Admin)**
premium_menu = InlineKeyboardMarkup()
premium_menu.add(InlineKeyboardButton("🎨 Buat Gambar", callback_data="generate_image"))
premium_menu.add(InlineKeyboardButton("🎙️ Kirim Suara", callback_data="voice_ai"))
premium_menu.add(InlineKeyboardButton("📂 Upload File", callback_data="upload_file"))
premium_menu.add(InlineKeyboardButton("📡 Cek Server", callback_data="cek_server"))
premium_menu.add(InlineKeyboardButton("🎥 Download YouTube", callback_data="download_yt"))
premium_menu.add(InlineKeyboardButton("📢 Kirim Broadcast", callback_data="broadcast"))
premium_menu.add(InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"))

# **🔹 Handler Start**
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    text = "🚀 Selamat datang di **Bot AI Ultra Fast**!\n\nPilih fitur yang ingin digunakan:"
    if user_id in ADMIN_IDS:
        await message.reply(text, reply_markup=premium_menu)
    else:
        await message.reply(text, reply_markup=menu)

# **🔹 Handler Chat AI**
@dp.callback_query_handler(lambda c: c.data == "chat_ai")
async def ask_chat_ai(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "💬 Ketik pertanyaanmu!")

@dp.message_handler()
async def handle_message(message: types.Message):
    response = await chat_ai(message.from_user.id, message.text)
    await message.reply(response)

# **🔹 Cek Cuaca**
@dp.callback_query_handler(lambda c: c.data == "cek_cuaca")
async def ask_cuaca(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "🌍 Ketik nama kota untuk cek cuaca!")

@dp.message_handler(lambda message: message.text.startswith("🌍"))
async def handle_cuaca(message: types.Message):
    city = message.text.replace("🌍", "").strip()
    api_url = f"http://api.weatherapi.com/v1/current.json?key=ISI_WEATHER_API&q={city}&aqi=no"
    data = requests.get(api_url).json()
    text = f"🌤 Cuaca di {city}:\n🌡 Suhu: {data['current']['temp_c']}°C\n💨 Angin: {data['current']['wind_kph']} km/h"
    await message.reply(text)

# **🔹 Kalkulator AI**
@dp.callback_query_handler(lambda c: c.data == "kalkulator")
async def ask_kalkulator(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "🧮 Kirim ekspresi matematika untuk dihitung!")

@dp.message_handler(lambda message: message.text.startswith("🧮"))
async def handle_kalkulator(message: types.Message):
    try:
        expression = message.text.replace("🧮", "").strip()
        result = eval(expression)
        await message.reply(f"✅ Hasil: {result}")
    except:
        await message.reply("❌ Format salah!")

# **🔹 Waktu Dunia**
@dp.callback_query_handler(lambda c: c.data == "waktu_dunia")
async def ask_waktu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "⏳ Ketik nama negara untuk cek waktu!")

@dp.message_handler(lambda message: message.text.startswith("⏳"))
async def handle_waktu(message: types.Message):
    country = message.text.replace("⏳", "").strip()
    timezone = pytz.timezone(f"Etc/GMT")
    now = datetime.now(timezone).strftime("%H:%M:%S")
    await message.reply(f"🕒 Waktu di {country}: {now}")

# **🔹 Add Admin**
@dp.callback_query_handler(lambda c: c.data == "add_admin")
async def ask_add_admin(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await bot.send_message(user_id, "❌ Maaf, hanya admin yang bisa menambah admin!")
        return
    await bot.send_message(user_id, "🆔 Kirim ID Telegram yang ingin dijadikan admin:")

@dp.message_handler(lambda message: message.text.isdigit())
async def handle_add_admin(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.reply("❌ Maaf, hanya admin yang bisa menambah admin!")
        return
    new_admin_id = int(message.text)
    if new_admin_id in ADMIN_IDS:
        await message.reply("⚠️ ID ini sudah menjadi admin!")
        return
    ADMIN_IDS.add(new_admin_id)
    await message.reply(f"✅ ID **{new_admin_id}** berhasil ditambahkan sebagai admin!")

# **🔹 Start Bot**
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
