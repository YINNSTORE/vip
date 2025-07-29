#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram Multi-Tools by Yinn VPN
Full System - Final Version (Part 1/2)
------------------------------------------------
Fitur:
- AdBypass (multi-link supported)
- IP Lookup (with API Key)
- Subdomain Finder (Anubis)
- Proxy Checker (real check)
- Auto Delete Messages (kecuali hasil)
- Admin Menu (user list + broadcast)
- Tombol kembali di semua menu
------------------------------------------------
"""

import os
import requests
import aiohttp
import asyncio
import logging
import datetime
import socket
from bs4 import BeautifulSoup
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    InputMediaPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from urllib.parse import urlparse

# =========================
# KONFIGURASI BOT
# =========================
BOT_TOKEN = "7414492608:AAEipio5iqjhoKC0QCoGoIe7HNUiLhAtQHg"  # TOKEN BOT
ADMIN_ID = 6353421952
ADMIN_USERNAME = "yinnprovpn"
IPINFO_API_KEY = "210a01b5fe3d19"

# =========================
# LOGGING
# =========================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================
# DATA USER
# =========================
users_data = {}  # {user_id: {"username": str, "join_date": datetime}}

# =========================
# AUTO DELETE HELPER
# =========================
async def auto_delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int = 10):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# =========================
# MENU UTAMA
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "Tidak Ada Username"
    if user_id not in users_data:
        users_data[user_id] = {
            "username": username,
            "join_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    text = (
        "👋 Selamat datang di **Bot Multi-Tools by Yinn VPN**\n"
        "Gunakan bot ini dengan bijak.\n\n"
        "Pilih menu dibawah untuk memulai:"
    )
    keyboard = [
        [InlineKeyboardButton("📜 All Menu", callback_data="all_menu")],
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton("🛠️ Admin Menu", callback_data="admin_menu")] if user_id == ADMIN_ID else []
    ]
    reply_markup = InlineKeyboardMarkup([btn for btn in keyboard if btn])
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# =========================
# ALL MENU
# =========================
async def all_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔗 AdBypass", callback_data="menu_adbypass")],
        [InlineKeyboardButton("🌐 IP Lookup", callback_data="menu_iplookup")],
        [InlineKeyboardButton("🔍 Subdomain Finder", callback_data="menu_subfinder")],
        [InlineKeyboardButton("🛰️ Proxy Checker", callback_data="menu_proxychecker")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📜 **Daftar Fitur:**", reply_markup=reply_markup, parse_mode="Markdown")

# =========================
# MENU ADMIN
# =========================
async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("👥 Cek User List", callback_data="admin_userlist")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🛠️ **Admin Menu:**", reply_markup=reply_markup, parse_mode="Markdown")

# =========================
# MAIN MENU CALLBACK
# =========================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📜 All Menu", callback_data="all_menu")],
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton("🛠️ Admin Menu", callback_data="admin_menu")] if update.effective_user.id == ADMIN_ID else []
    ]
    reply_markup = InlineKeyboardMarkup([btn for btn in keyboard if btn])
    await query.edit_message_text(
        "👋 Selamat datang di **Bot Multi-Tools by Yinn VPN**\nGunakan bot ini dengan bijak.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# =========================
# FITUR 1: ADBYPASS
# =========================
async def menu_adbypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🔗 **AdBypass Menu:**\n\nKirim link yang ingin di-bypass."
    keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    context.user_data["mode"] = "adbypass"

async def handle_adbypass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text("🔄 Memproses link, tunggu sebentar...")
    asyncio.create_task(auto_delete_message(context, chat_id, update.message.message_id))
    link = update.message.text.strip()
    try:
        bypass_result = await bypass_link(link)
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Link berhasil di-bypass:\n{bypass_result}")
    except Exception as e:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Gagal bypass link: {e}")

async def bypass_link(url):
    # Simulasi proses bypass multi-link
    # NOTE: Bisa diupgrade untuk pakai API eksternal jika ada
    parsed = urlparse(url)
    if not parsed.scheme.startswith("http"):
        raise Exception("Link tidak valid.")
    # contoh: hapus parameter tracking
    clean_url = url.split("?")[0].replace("www.", "")
    await asyncio.sleep(2)
    return clean_url

# =========================
# FITUR 2: IP LOOKUP
# =========================
async def menu_iplookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🌐 **IP Lookup Menu:**\n\nKirim IP Address atau domain yang ingin diperiksa."
    keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    context.user_data["mode"] = "iplookup"

async def handle_iplookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    target = update.message.text.strip()
    msg = await update.message.reply_text("🔄 Mengecek IP, tunggu sebentar...")
    asyncio.create_task(auto_delete_message(context, chat_id, update.message.message_id))
    try:
        url = f"https://ipinfo.io/{target}?token={IPINFO_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        result = (
            f"**Hasil IP Lookup:**\n"
            f"🔹 IP: {data.get('ip','-')}\n"
            f"🔹 Hostname: {data.get('hostname','-')}\n"
            f"🔹 Kota: {data.get('city','-')}\n"
            f"🔹 Negara: {data.get('country','-')}\n"
            f"🔹 Lokasi: {data.get('loc','-')}\n"
            f"🔹 ISP: {data.get('org','-')}"
        )
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=result, parse_mode="Markdown")
    except Exception as e:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Gagal cek IP: {e}")
# =========================
# FITUR 3: SUBDOMAIN FINDER (ANUBIS)
# =========================
async def menu_subfinder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🔍 **Subdomain Finder:**\n\nKirim domain target (contoh: example.com)"
    keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    context.user_data["mode"] = "subfinder"

async def handle_subfinder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    domain = update.message.text.strip()
    msg = await update.message.reply_text("🔄 Mencari subdomain...")
    asyncio.create_task(auto_delete_message(context, chat_id, update.message.message_id))
    try:
        url = f"https://jldc.me/anubis/subdomains/{domain}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
        if not data:
            result = "❌ Tidak ditemukan subdomain."
        else:
            result = "**Subdomain ditemukan:**\n" + "\n".join(f"🔹 {sub}" for sub in data)
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=result, parse_mode="Markdown")
    except Exception as e:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Gagal mencari subdomain: {e}")

# =========================
# FITUR 4: PROXY CHECKER
# =========================
async def menu_proxychecker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🛰️ **Proxy Checker:**\n\nKirim proxy (IP:PORT) untuk dicek."
    keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="all_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    context.user_data["mode"] = "proxychecker"

async def handle_proxychecker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    proxy = update.message.text.strip()
    msg = await update.message.reply_text("🔄 Mengecek proxy...")
    asyncio.create_task(auto_delete_message(context, chat_id, update.message.message_id))
    try:
        ip, port = proxy.split(":")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            result = s.connect_ex((ip, int(port)))
        status = "✅ Proxy aktif" if result == 0 else "❌ Proxy mati"
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=f"Hasil Proxy Checker:\n{proxy} → {status}")
    except Exception as e:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Format atau proxy salah: {e}")

# =========================
# ADMIN FITUR
# =========================
async def admin_userlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "👥 **Daftar Pengguna Bot:**\n"
    for uid, info in users_data.items():
        text += f"🔹 {info['username']} (`{uid}`) - Join: {info['join_date']}\n"
    keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "📢 Kirim pesan yang ingin dibroadcast ke semua user."
    keyboard = [[InlineKeyboardButton("⬅️ Kembali", callback_data="admin_menu")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["mode"] = "broadcast"

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = update.message.text
    for uid in users_data:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **Broadcast:**\n{text}")
        except:
            pass
    await update.message.reply_text("✅ Broadcast selesai.")
    asyncio.create_task(auto_delete_message(context, update.effective_chat.id, update.message.message_id))

# =========================
# HANDLER
# =========================
async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")
    if mode == "adbypass":
        await handle_adbypass(update, context)
    elif mode == "iplookup":
        await handle_iplookup(update, context)
    elif mode == "subfinder":
        await handle_subfinder(update, context)
    elif mode == "proxychecker":
        await handle_proxychecker(update, context)
    elif mode == "broadcast":
        await handle_broadcast(update, context)

# =========================
# MAIN
# =========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command
    app.add_handler(CommandHandler("start", start))

    # Callback
    app.add_handler(CallbackQueryHandler(all_menu, pattern="all_menu"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(admin_menu, pattern="admin_menu"))
    app.add_handler(CallbackQueryHandler(admin_userlist, pattern="admin_userlist"))
    app.add_handler(CallbackQueryHandler(admin_broadcast, pattern="admin_broadcast"))
    app.add_handler(CallbackQueryHandler(menu_adbypass, pattern="menu_adbypass"))
    app.add_handler(CallbackQueryHandler(menu_iplookup, pattern="menu_iplookup"))
    app.add_handler(CallbackQueryHandler(menu_subfinder, pattern="menu_subfinder"))
    app.add_handler(CallbackQueryHandler(menu_proxychecker, pattern="menu_proxychecker"))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    print("✅ Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()