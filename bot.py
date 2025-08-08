import logging
import requests
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# ====== CONFIG ======
BOT_TOKEN = "8219112088:AAGKuWaiRrSeHwUK_8wCeuDY2GHFYkFsLdI"  # Ganti token dari @BotFather

# ====== SETUP ======
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ====== BUTTONS ======
def menu_buttons():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📥 TikTok", callback_data="tiktok"),
        InlineKeyboardButton("▶️ YouTube", callback_data="youtube"),
        InlineKeyboardButton("📷 Instagram", callback_data="instagram"),
        InlineKeyboardButton("📘 Facebook", callback_data="facebook"),
    )
    return kb

# ====== TIKTOK API (TIKMATE) ======
def download_tiktok(url):
    match = re.search(r"/video/(\d+)", url)
    if not match:
        return None

    video_id = match.group(1)
    api_url = f"https://api.tikmate.app/api/lookup?id={video_id}"
    try:
        res = requests.get(api_url).json()
        if "token" not in res:
            return None

        video_url = f"https://tikmate.app/download/{res['token']}/{res['id']}.mp4"
        return {
            "title": "Video by @" + res.get("author_name", "unknown"),
            "video_url": video_url,
            "platform": "TikTok"
        }
    except:
        return None

# ====== SAVEFROM API (YT/FB/IG) ======
def download_savefrom(url):
    try:
        api_url = "https://api.savefrom.net/1/info"
        res = requests.get(api_url, params={"url": url, "lang": "en"}).json()

        if res.get("url") and res.get("meta"):
            return {
                "title": res["meta"].get("title", "Untitled"),
                "video_url": res["url"],
                "platform": res["meta"].get("source", "Unknown")
            }
        return None
    except:
        return None

# ====== COMMAND /start ======
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.reply(
        "👋 *Selamat datang di Video Downloader Bot!*\n\nKamu bisa kirim link langsung atau pilih platform dulu:",
        reply_markup=menu_buttons(),
        parse_mode="Markdown"
    )

# ====== BUTTON HANDLER ======
@dp.callback_query_handler(lambda c: c.data in ["tiktok", "youtube", "instagram", "facebook"])
async def handle_button(callback_query: types.CallbackQuery):
    platform = callback_query.data
    await bot.send_message(callback_query.from_user.id, f"✅ Sekarang kirim link dari *{platform.title()}*", parse_mode="Markdown")

# ====== LINK HANDLER ======
@dp.message_handler()
async def handle_link(msg: types.Message):
    url = msg.text.strip()

    if "tiktok.com" in url:
        await msg.reply("⏳ Mengambil video dari TikTok...")
        result = download_tiktok(url)
    elif any(x in url for x in ["youtu", "facebook.com", "fb.watch", "instagram.com", "reel"]):
        await msg.reply("⏳ Mengambil video dari SaveFrom...")
        result = download_savefrom(url)
    else:
        await msg.reply("❗ Kirim link dari TikTok, YouTube, Facebook, atau Instagram.")
        return

    if result:
        try:
            await bot.send_video(
                msg.chat.id,
                video=result["video_url"],
                caption=f"🎬 *{result['title']}*\n📌 Platform: {result['platform']}",
                parse_mode="Markdown"
            )
        except:
            await msg.reply(f"✅ Video terlalu besar dikirim.\n🔗 [Klik untuk download langsung]({result['video_url']})", parse_mode="Markdown", disable_web_page_preview=True)
    else:
        await msg.reply("❌ Gagal mengambil video. Link tidak valid atau diblokir.")

# ====== START BOT ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)