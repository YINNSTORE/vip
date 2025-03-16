import logging
import os
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Token bot Telegram
TOKEN = "ISI_TOKEN_BOT_KAMU"

# Direktori penyimpanan file sementara
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Inisialisasi bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Log
logging.basicConfig(level=logging.INFO)

# Tombol daftar decrypt
decrypt_menu = InlineKeyboardMarkup(row_width=2)
decrypt_menu.add(
    InlineKeyboardButton("🔑 SHC", callback_data="decrypt_shc"),
    InlineKeyboardButton("🔑 BashRock", callback_data="decrypt_bashrock"),
    InlineKeyboardButton("🔑 Eval", callback_data="decrypt_eval"),
    InlineKeyboardButton("🔑 Base64", callback_data="decrypt_base64"),
    InlineKeyboardButton("🔑 Base64 Eval", callback_data="decrypt_base64eval"),
)

# Command /start
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    text = (
        "🚀 Kirim file bash yang akan di-decrypt\n"
        "⚙️ **Daftar yang bisa di-decrypt bot:**\n"
        "1️⃣ SHC\n"
        "2️⃣ BashRock\n"
        "3️⃣ Eval\n"
        "4️⃣ Base64\n"
        "5️⃣ Base64Eval\n"
        "❌ Bzip2 dan Gzip belum support\n"
    )
    await msg.reply(text, reply_markup=decrypt_menu, parse_mode="Markdown")

# Handler untuk menerima file bash
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def receive_file(message: types.Message):
    file_id = message.document.file_id
    file_name = message.document.file_name

    # Cek apakah file berekstensi .sh
    if not file_name.endswith(".sh"):
        await message.reply("❌ File harus berformat .sh")
        return

    # Unduh file
    file_path = os.path.join(TEMP_DIR, file_name)
    await message.document.download(destination_file=file_path)

    # Cek apakah file terenkripsi
    decrypted_file_path = decrypt_bash(file_path)
    
    if decrypted_file_path:
        # Kirim hasil decrypt ke pengguna
        with open(decrypted_file_path, "rb") as f:
            await bot.send_document(message.chat.id, f)
        
        await message.reply("✅ Done!", parse_mode="Markdown")
    else:
        await message.reply("❌ Gagal decrypt file.")

# Fungsi decrypt file Bash
def decrypt_bash(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Deteksi jenis enkripsi
        if "shc" in content:
            return decrypt_shc(file_path)
        elif "base64" in content:
            return decrypt_base64(file_path)
        elif "eval" in content:
            return decrypt_eval(file_path)
        else:
            return None
    except Exception as e:
        logging.error(f"Error decrypting file: {e}")
        return None

# Fungsi decrypt SHC
def decrypt_shc(file_path):
    output_path = file_path.replace(".sh", "_decrypted.sh")
    cmd = f"unshc {file_path} -o {output_path}"  # Harus install unshc
    subprocess.run(cmd, shell=True)
    return output_path if os.path.exists(output_path) else None

# Fungsi decrypt Base64
def decrypt_base64(file_path):
    output_path = file_path.replace(".sh", "_decrypted.sh")
    cmd = f"base64 -d {file_path} > {output_path}"
    subprocess.run(cmd, shell=True)
    return output_path if os.path.exists(output_path) else None

# Fungsi decrypt Eval
def decrypt_eval(file_path):
    output_path = file_path.replace(".sh", "_decrypted.sh")
    cmd = f"sed 's/eval//g' {file_path} > {output_path}"
    subprocess.run(cmd, shell=True)
    return output_path if os.path.exists(output_path) else None

# Jalankan bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
