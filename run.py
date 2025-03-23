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
    [InlineKeyboardButton("💬 Chat AI", callback_data="chat_ai")],
    [InlineKeyboardButton("🌎 Translate", callback_data="translate")],
    [InlineKeyboardButton("📖 Quotes", callback_data="quotes")],
    [InlineKeyboardButton("🕒 Waktu Dunia", callback_data="waktu_dunia")]
])

premium_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton("🎨 Buat Gambar", callback_data="generate_image")],
    [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin")]
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

# **🔹 Chat AI (Fast Response)**
async def chat_ai(user_id, prompt):
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({"role": "user", "content": prompt})

    response = await asyncio.to_thread(openai.ChatCompletion.create,
        model="gpt-4-turbo",
        messages=user_memory[user_id]
    )

    reply_text = response["choices"][0]["message"]["content"]
    user_memory[user_id].append({"role": "assistant", "content": reply_text})

    return reply_text

@dp.message()
async def handle_chat(message: types.Message):
    response = await chat_ai(message.from_user.id, message.text)
    await message.answer(response)

# **🔹 Translate**
@dp.callback_query(lambda c: c.data == "translate")
async def ask_translate(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "🌍 Ketik teks yang ingin diterjemahkan ke Inggris!")

@dp.message(lambda message: message.text.startswith("🌍"))
async def handle_translate(message: types.Message):
    text = message.text.replace("🌍", "").strip()
    translation = await chat_ai(message.from_user.id, f"Translate ke Inggris: {text}")
    await message.reply(f"🔠 Terjemahan: {translation}")

# **🔹 Quotes AI**
@dp.callback_query(lambda c: c.data == "quotes")
async def handle_quotes(callback_query: types.CallbackQuery):
    quote = await chat_ai(callback_query.from_user.id, "Beri saya satu quotes motivasi.")
    await bot.send_message(callback_query.from_user.id, f"📖 {quote}")

# **🔹 Waktu Dunia**
@dp.callback_query(lambda c: c.data == "waktu_dunia")
async def ask_waktu(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "⏳ Ketik nama negara untuk cek waktu!")

@dp.message(lambda message: message.text.startswith("⏳"))
async def handle_waktu(message: types.Message):
    country = message.text.replace("⏳", "").strip()
    timezone = pytz.timezone("Etc/GMT")
    now = datetime.now(timezone).strftime("%H:%M:%S")
    await message.reply(f"🕒 Waktu di {country}: {now}")

# **🔹 Add Admin**
@dp.callback_query(lambda c: c.data == "add_admin")
async def ask_add_admin(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMIN_IDS:
        await bot.send_message(user_id, "❌ Hanya admin yang bisa menambah admin!")
        return
    await bot.send_message(user_id, "🆔 Kirim ID Telegram yang ingin dijadikan admin:")

@dp.message(lambda message: message.text.isdigit())
async def handle_add_admin(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        await message.reply("❌ Hanya admin yang bisa menambah admin!")
        return
    new_admin_id = int(message.text)
    if new_admin_id in ADMIN_IDS:
        await message.reply("⚠️ ID ini sudah admin!")
        return
    ADMIN_IDS.add(new_admin_id)
    await message.reply(f"✅ ID **{new_admin_id}** berhasil ditambahkan sebagai admin!")

# **🔹 Jalankan Bot**
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
