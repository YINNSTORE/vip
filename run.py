import os
import shutil
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Tombol keyboard
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("📂 Kirim File Bash"))

# Fungsi untuk mendeteksi enkripsi
def deteksi_enkripsi(file_path):
    with open(file_path, "r", encoding="latin-1") as f:
        content = f.read()

    if "shc" in content:
        return "shc"
    elif "base64" in content and "eval" in content:
        return "base64eval"
    elif "base64" in content:
        return "base64"
    elif "eval" in content:
        return "eval"
    elif "BashRock" in content:
        return "bashrock"
    else:
        return "unknown"

# Fungsi untuk mendekripsi file
def decrypt_file(file_path, encryption_type):
    decrypted_file = file_path + ".decrypted.sh"
    
    try:
        if encryption_type == "shc":
            decrypted_file = file_path.replace(".sh.x.c", ".sh")
            subprocess.run(["unshc", "-f", file_path], check=True)
        
        elif encryption_type == "base64":
            with open(file_path, "r") as f:
                encoded_content = f.read()
            decoded_content = subprocess.run(["base64", "-d"], input=encoded_content.encode(), capture_output=True, text=True).stdout
            with open(decrypted_file, "w") as f:
                f.write(decoded_content)
        
        elif encryption_type == "base64eval":
            with open(file_path, "r") as f:
                content = f.read().replace("eval", "").replace("base64", "")
            decoded_content = subprocess.run(["base64", "-d"], input=content.encode(), capture_output=True, text=True).stdout
            with open(decrypted_file, "w") as f:
                f.write(decoded_content)

        elif encryption_type == "eval":
            with open(file_path, "r") as f:
                content = f.read().replace("eval", "")
            with open(decrypted_file, "w") as f:
                f.write(content)

        elif encryption_type == "bashrock":
            decrypted_file = file_path.replace(".bashrock", ".sh")
            subprocess.run(["bash", "-c", f"bash_decrypt {file_path} > {decrypted_file}"], check=True)

        else:
            return None
    
        return decrypted_file

    except Exception as e:
        return None

# Handler untuk /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("🚀 Kirim file bash yang akan di-decrypt\n⚙️ Bot akan otomatis mendeteksi dan mendekripsi!", reply_markup=keyboard)

# Handler untuk menerima file
@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_file(message: types.Message):
    file_id = message.document.file_id
    file_name = message.document.file_name
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    local_file_path = f"./{file_name}"

    await message.document.download(destination_file=local_file_path)
    
    encryption_type = deteksi_enkripsi(local_file_path)

    if encryption_type == "unknown":
        await message.reply("⚠️ File tidak terdeteksi memiliki enkripsi yang didukung!")
        os.remove(local_file_path)
        return

    await message.reply(f"🔍 Detected Encryption: **{encryption_type.upper()}**\n⏳ Processing Decryption...")

    decrypted_file = decrypt_file(local_file_path, encryption_type)

    if decrypted_file:
        await message.reply_document(open(decrypted_file, "rb"), caption="✅ Decryption Success!")
        os.remove(decrypted_file)
    else:
        await message.reply("❌ Gagal mendekripsi file!")

    os.remove(local_file_path)

# Jalankan bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
