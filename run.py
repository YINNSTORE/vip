import os
import subprocess
from pyrogram import Client, filters

# Ganti dengan API ID, API HASH, dan BOT TOKEN dari @BotFather
API_ID = "6353421952"
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"

if not os.path.exists("downloads"):
    os.makedirs("downloads")

def detect_encryption(file_path):
    if file_path.endswith(".sh.x"):
        return "BashArmor"
    elif file_path.endswith(".bz2"):
        return "BZip2"
    elif file_path.endswith(".shc"):
        return "SHC"
    elif file_path.endswith(".basrock"):
        return "Basrock"
    else:
        return "Unknown"

def encrypt_file(file_path, method):
    output_file = file_path
    if method == "SHC":
        output_file = file_path + ".shc"
        subprocess.run(["shc", "-f", file_path, "-o", output_file])
    elif method == "BZip2":
        subprocess.run(["bzip2", file_path])
        output_file = file_path + ".bz2"
    elif method == "BashArmor":
        output_file = file_path + ".sh.x"
        subprocess.run(["basharmor", file_path, "-o", output_file])
    elif method == "Basrock":
        output_file = file_path + ".basrock"
        subprocess.run(["basrock", "encrypt", "-i", file_path, "-o", output_file])
    return output_file

def decrypt_file(file_path, method):
    output_file = file_path.replace(".sh.x", "").replace(".bz2", "").replace(".shc", "").replace(".basrock", "")
    if method == "BZip2":
        subprocess.run(["bzip2", "-d", file_path])
        output_file = file_path[:-4]
    elif method == "Basrock":
        subprocess.run(["basrock", "decrypt", "-i", file_path, "-o", output_file])
    return output_file

def install_dependencies():
    dependencies = ["shc", "bzip2", "basharmor", "basrock"]

    # Check for package installation and install if not present
    for dep in dependencies:
        try:
            print(f"⏳ Checking if {dep} is installed...")
            result = subprocess.run(["dpkg", "-s", dep], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                print(f"{dep} not found. Installing {dep}...")
                subprocess.run(["sudo", "apt-get", "update", "-y"])
                subprocess.run(["sudo", "apt-get", "install", "-y", dep])
                print(f"✅ {dep} installed successfully!")
            else:
                print(f"✅ {dep} is already installed.")
        except Exception as e:
            print(f"❌ Error installing {dep}: {str(e)}")

bot = Client("encrypt_decrypt_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

last_sent_file = None

@bot.on_message(filters.command("/start"))
async def start(client, message):
    await message.reply_text("🔐 *Bot Enkripsi & Dekripsi*\n\n"
                             "Kirim file untuk dienkripsi atau didekripsi.\n"
                             "Gunakan /encrypt <metode> atau /decrypt.")

@bot.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message):
    global last_sent_file
    file_path = f"downloads/{message.document.file_name if message.document else 'image.jpg'}"
    await message.reply_text("📥 Mengunduh file...")
    await bot.download_media(message, file_path)
    last_sent_file = file_path
    await message.reply_text(f"✅ File berhasil diunduh: {file_path}\n"
                             "Gunakan /encrypt atau /decrypt untuk memproses file.")

@bot.on_message(filters.command("encrypt"))
async def encrypt(client, message):
    global last_sent_file
    if not last_sent_file:
        await message.reply_text("❌ Tidak ada file yang diupload. Kirimkan file terlebih dahulu!")
        return

    method = message.text.split()[1] if len(message.text.split()) > 1 else None
    if not method:
        await message.reply_text("❌ Gunakan format: `/encrypt <SHC|BZip2|BashArmor|Basrock>`", parse_mode="markdown")
        return

    if method not in ["SHC", "BZip2", "BashArmor", "Basrock"]:
        await message.reply_text("❌ Pilihan enkripsi tidak valid! Pilih: SHC, BZip2, BashArmor, atau Basrock.")
        return

    encrypted_file = encrypt_file(last_sent_file, method)
    await message.reply_text(f"🔐 File berhasil dienkripsi menggunakan {method}. Mengirim file terenkripsi...")
    await bot.send_document(message.chat.id, encrypted_file, caption=f"✅ File terenkripsi dengan {method}")
    os.remove(encrypted_file)

@bot.on_message(filters.command("decrypt"))
async def decrypt(client, message):
    global last_sent_file
    if not last_sent_file:
        await message.reply_text("❌ Tidak ada file yang diupload. Kirimkan file terlebih dahulu!")
        return

    encryption_method = detect_encryption(last_sent_file)
    if encryption_method == "Unknown":
        await message.reply_text("❌ Jenis enkripsi file tidak dikenali!")
        return

    decrypted_file = decrypt_file(last_sent_file, encryption_method)
    await message.reply_text(f"🔓 File berhasil didekripsi menggunakan {encryption_method}. Mengirim file terdekripsi...")
    await bot.send_document(message.chat.id, decrypted_file, caption="✅ File terdekripsi!")
    os.remove(decrypted_file)

@bot.on_message(filters.command("execute"))
async def execute(client, message):
    global last_sent_file
    if not last_sent_file:
        await message.reply_text("❌ Tidak ada file yang dieksekusi. Kirimkan file terlebih dahulu!")
        return

    file_path = last_sent_file
    os.chmod(file_path, 0o755)

    try:
        result = subprocess.run(file_path, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        await message.reply_text(f"🖥️ Output eksekusi:\n\n```\n{output}\n```", parse_mode="markdown")
    except Exception as e:
        await message.reply_text(f"❌ Gagal mengeksekusi file!\nError: {str(e)}")

if __name__ == "__main__":
    install_dependencies()  # Install dependencies before starting bot
    bot.run()