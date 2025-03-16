import asyncio
import os
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# Ganti dengan token bot Telegram kamu
TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Fungsi untuk mendeteksi jenis enkripsi
def detect_encryption(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "shc" in content:
                return "shc"
            elif "bashrock" in content:
                return "bashrock"
            elif "eval" in content:
                return "eval"
            elif "base64" in content:
                return "base64"
            else:
                return "unknown"
    except Exception as e:
        return f"error: {str(e)}"

# Fungsi untuk dekripsi berdasarkan jenis enkripsi
def decrypt_file(file_path, encryption_type):
    output_path = file_path.replace(".sh", "_decrypted.sh")
    
    if encryption_type == "shc":
        cmd = f"unshc -f {file_path} -o {output_path}"
    elif encryption_type == "bashrock":
        cmd = f"bashrock -d {file_path} -o {output_path}"
    elif encryption_type == "eval":
        cmd = f"cat {file_path} | sed 's/eval /echo /g' > {output_path}"
    elif encryption_type == "base64":
        cmd = f"base64 -d {file_path} > {output_path}"
    else:
        return None

    try:
        subprocess.run(cmd, shell=True, check=True)
        return output_path
    except subprocess.CalledProcessError:
        return None

# Start command
@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Kirim File untuk Decrypt", callback_data="send_file")],
        [InlineKeyboardButton(text="🔄 Bantuan", callback_data="help")]
    ])
    await message.answer("🚀 Kirim file bash (.sh) untuk di-decrypt!", reply_markup=keyboard)

# Handle file upload
@dp.message(lambda message: message.document and message.document.mime_type == "application/x-sh")
async def handle_file(message: types.Message):
    file_id = message.document.file_id
    file_name = message.document.file_name

    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_name}"

    await bot.download_file(file.file_path, file_path)
    encryption_type = detect_encryption(file_path)

    if encryption_type == "unknown":
        await message.answer("❌ File tidak terdeteksi memiliki enkripsi yang didukung.")
        return

    decrypted_file = decrypt_file(file_path, encryption_type)
    if decrypted_file:
        await message.answer("✅ File berhasil didekripsi! Mengirim file...")
        await message.answer_document(FSInputFile(decrypted_file))
        os.remove(file_path)
        os.remove(decrypted_file)
    else:
        await message.answer("❌ Gagal mendekripsi file!")

# Help command
@dp.callback_query(lambda c: c.data == "help")
async def help_callback(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "📜 Cara penggunaan:\n"
        "1. Kirim file `.sh` yang ingin di-decrypt.\n"
        "2. Bot akan otomatis mendeteksi jenis enkripsi.\n"
        "3. Jika berhasil, bot akan mengirim file hasil dekripsi.\n\n"
        "🔧 Format yang didukung: SHC, BashRock, Eval, Base64."
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    asyncio.run(main())
