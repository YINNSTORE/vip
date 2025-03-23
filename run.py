import os
import openai
import asyncio
import logging
import requests
import pytz
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# **🔹 API Key**
BOT_TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"
OPENAI_API_KEY = ""

# **🔹 ID Admin Awal**
ADMIN_IDS = {6353421952}  # Ganti dengan ID Admin pertama

# **🔹 Inisialisasi bot & OpenAI**
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

openai.api_key = OPENAI_API_KEY
user_memory = {}  # Simpan percakapan per user

# **🔹 Keyboard Menu**
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💬 Chat AI", callback_data="chat_ai")],
    [InlineKeyboardButton(text="🌎 Translate", callback_data="translate")],
    [InlineKeyboardButton(text="📖 Quotes", callback_data="quotes")],
    [InlineKeyboardButton(text="🕒 Waktu Dunia", callback_data="waktu_dunia")]
])

premium_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎨 Buat Gambar", callback_data="generate_image")],
    [InlineKeyboardButton(text="➕ Add Admin", callback_data="add_admin")]
])

# **🔹 Menu Utama**
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    text = (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🧿 *SELAMAT DATANG DI BOT CHATGPT* 🧿\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🤖 *Bot ini menggunakan ChatGPT AI*\n"
        "💬 Ketik pesan apa saja untuk bertanya!\n"
        "📌 Gunakan tombol di bawah untuk fitur tambahan.\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    keyboard = premium_menu if user_id in ADMIN_IDS else menu
    await message.answer(text, reply_markup=keyboard)

# **🔹 Jalankan Bot**
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
