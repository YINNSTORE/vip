import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔹 API Telegram Bot & Admin ID
API_ID = 21635979  
API_HASH = "cbc12884284bc3457360ca9b9d37b94e"
BOT_TOKEN = "7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"
ADMIN_ID = "6353421952"  # Ganti dengan ID admin

bot = Client("app_builder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Fungsi Kirim Notifikasi ke Telegram Admin
def notify_admin(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_ID, "text": message}
    requests.post(url, data=data)

# 🔹 Fungsi Cek Dependensi Buildozer
def check_dependencies():
    dependencies = ["buildozer", "python3", "pip", "git"]
    missing = [pkg for pkg in dependencies if os.system(f"command -v {pkg} > /dev/null 2>&1") != 0]
    
    if missing:
        return f"❌ Dependensi belum terinstall: {', '.join(missing)}\nHarap install dengan:\n`apt install -y {' '.join(missing)}`"
    return None

# 🔹 Saat user /start, tampilkan menu pilihan
@bot.on_message(filters.private & filters.command("start"))
def start(client, message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛠 Buat Aplikasi", callback_data="buat_aplikasi")],
        [InlineKeyboardButton("🎮 Buat Game", callback_data="buat_game")]
    ])
    message.reply_text("🚀 Pilih jenis yang ingin dibuat:", reply_markup=keyboard)

# 🔹 Menangani tombol yang ditekan user
@bot.on_callback_query()
def callback_handler(client, callback_query):
    if callback_query.data == "buat_aplikasi":
        callback_query.message.reply_text("✍️ Kirim nama aplikasi yang ingin dibuat:")
    elif callback_query.data == "buat_game":
        callback_query.message.reply_text("✍️ Kirim nama game yang ingin dibuat:")

# 🔹 Proses pembuatan aplikasi/game setelah user kirim nama
@bot.on_message(filters.private & filters.text)
async def create_app(client, message):
    app_name = message.text.replace(" ", "_")
    chat_id = message.chat.id
    user_id = message.from_user.id

    # 🔹 Cek dependensi sebelum build
    missing_packages = check_dependencies()
    if missing_packages:
        await bot.send_message(chat_id, missing_packages)
        return

    # 🔹 Buat folder aplikasi
    app_dir = f"/tmp/{app_name}"
    os.makedirs(app_dir, exist_ok=True)

    # 🔹 Buat file main.py (kode aplikasi/game)
    main_py = f"""
from kivy.app import App
from kivy.uix.button import Button

class MyApp(App):
    def build(self):
        return Button(text="Hello, {app_name}!", size_hint=(0.5, 0.5), pos_hint={{"center_x": 0.5, "center_y": 0.5}})

MyApp().run()
"""
    with open(f"{app_dir}/main.py", "w") as f:
        f.write(main_py)

    await bot.send_message(chat_id, f"📦 Membuat aplikasi '{app_name}'...")

    # 🔹 Buat file buildozer.spec (config untuk Buildozer)
    buildozer_spec = f"""
[app]
title = {app_name}
package.name = {app_name.lower()}
package.domain = org.example
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy
android.api = 29
android.ndk_api = 21
android.arch = arm64-v8a
"""
    with open(f"{app_dir}/buildozer.spec", "w") as f:
        f.write(buildozer_spec)

    await bot.send_message(chat_id, "⚙️ Mulai proses build APK... (Ini bisa memakan waktu lama)")

    # 🔹 Jalankan Buildozer untuk compile APK
    build_command = f"cd {app_dir} && buildozer -v android debug"
    process = await asyncio.create_subprocess_shell(build_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    progress_msg = await bot.send_message(chat_id, "⏳ Progress: 0%")
    progress = 0

    while True:
        line = await process.stdout.readline()
        if not line:
            break
        output = line.decode().strip()

        # 🔹 Update progress berdasarkan output Buildozer
        if "Check configuration tokens" in output:
            progress = 10
        elif "Preparing build" in output:
            progress = 20
        elif "Compiling source" in output:
            progress = 50
        elif "Packaging" in output:
            progress = 80
        elif "BUILD SUCCESSFUL" in output:
            progress = 100

        await progress_msg.edit_text(f"⏳ Progress: {progress}%")

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        apk_path = f"{app_dir}/bin/{app_name}.apk"
        if os.path.exists(apk_path):
            await bot.send_document(chat_id, apk_path, caption="✅ Aplikasi berhasil dibuat!")
            notify_admin(f"📱 APK '{app_name}' telah dibuat oleh user {user_id}!")
        else:
            await bot.send_message(chat_id, "❌ Gagal membuat APK.")
            notify_admin(f"⚠️ Gagal membuat APK untuk {app_name} oleh user {user_id}.")
    else:
        await bot.send_message(chat_id, f"❌ Terjadi kesalahan saat build APK:\n{stderr.decode()}")
        notify_admin(f"⚠️ ERROR Build APK {app_name} oleh user {user_id}.\n{stderr.decode()}")

bot.run()
