# nokos_full_buttons.py
"""
Nokos OTP Bot - Versi Full (Semua Tombol, Bahasa Indonesia)
- Semua menu via InlineKeyboard (User + Admin step-by-step)
- DummyProvider mensimulasikan nomor & OTP (aman untuk testing)
- SQLite menyimpan users, numbers, messages, saldo/limit
- Admin actions via tombol: Add Saldo, Set Premium, Broadcast, Daftar User
- Pemrosesan input admin (mis. jumlah topup, pesan broadcast) via message hooks
"""

import asyncio
import logging
import random
import sqlite3
from datetime import datetime
from typing import Callable, Dict, List, Optional, Tuple

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"
ADMIN_ID = 6353421952
DEV_USERNAME = "@yinnprovpn"
BANNER_URL = "https://awy.my.id/uploads/ini-linkfoto-baner.jpeg"
DB_FILE = "nokos_full_bot.db"

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        role TEXT DEFAULT 'member',
        status TEXT DEFAULT 'free',
        limit_count INTEGER DEFAULT 3
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        number TEXT,
        provider TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number_id INTEGER,
        text TEXT,
        received_at TEXT
    )""")
    conn.commit()
    conn.close()

def get_user(user_id:int) -> Optional[Tuple]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role, status, limit_count FROM users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    conn.close()
    return r

def ensure_user(user_id:int, username:str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if not get_user(user_id):
        role = "admin" if user_id == ADMIN_ID else "member"
        limit = None if role == "admin" else 3
        cur.execute("INSERT INTO users (user_id, username, role, status, limit_count) VALUES (?,?,?,?,?)",
                    (user_id, username, role, "free", limit))
        conn.commit()
    conn.close()

def list_users(limit:int=50) -> List[Tuple]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role, status, limit_count FROM users ORDER BY rowid DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def update_user_limit(user_id:int, new_limit:Optional[int]):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE users SET limit_count=? WHERE user_id=?", (new_limit, user_id))
    conn.commit()
    conn.close()

def set_user_status(user_id:int, status:str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if status == "premium":
        cur.execute("UPDATE users SET status=?, limit_count=NULL WHERE user_id=?", (status, user_id))
    else:
        cur.execute("UPDATE users SET status=?, limit_count=? WHERE user_id=?", (status, 3, user_id))
    conn.commit()
    conn.close()

# numbers & messages
def add_number_for_user(user_id:int, number:str, provider:str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO numbers (user_id, number, provider, active, created_at) VALUES (?,?,?,?,?)",
                (user_id, number, provider, 1, datetime.utcnow().isoformat()))
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    return nid

def get_active_number(user_id:int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, number, provider FROM numbers WHERE user_id=? AND active=1 ORDER BY id DESC LIMIT 1", (user_id,))
    r = cur.fetchone()
    conn.close()
    return r

def deactivate_number_by_id(nid:int):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE numbers SET active=0 WHERE id=?", (nid,))
    conn.commit()
    conn.close()

def add_message(number_id:int, text:str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (number_id, text, received_at) VALUES (?,?,?)",
                (number_id, text, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def list_messages_for_user(user_id:int) -> List[Tuple]:
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
       SELECT m.text, m.received_at, n.number
       FROM messages m
       JOIN numbers n ON m.number_id = n.id
       WHERE n.user_id = ?
       ORDER BY m.id DESC
       LIMIT 100
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- PROVIDER (Dummy) ----------------
class DummyProvider:
    def __init__(self):
        self.pool = [f"+10000000{str(i).zfill(3)}" for i in range(1, 401)]
        self._tasks: Dict[str, asyncio.Task] = {}

    async def list_available_numbers(self) -> List[str]:
        await asyncio.sleep(0.05)
        # safe: return random subset
        return random.sample(self.pool, k=8)

    async def start_monitor(self, number:str, on_message: Callable[[str], None]):
        # simulate random OTP messages; on_message is sync or async wrapper
        async def sim():
            # first message delay a bit
            await asyncio.sleep(random.randint(5, 12))
            while True:
                await asyncio.sleep(random.randint(8, 25))
                otp = f"{random.randint(100000, 999999)}"
                text = f"Kode verifikasi: {otp}\nJangan berikan ke siapa pun."
                try:
                    on_message(text)
                except Exception:
                    pass
        task = asyncio.create_task(sim())
        self._tasks[number] = task
        return task

    def stop(self, number:str):
        t = self._tasks.get(number)
        if t:
            t.cancel()

provider = DummyProvider()
# map number_id -> task
monitor_map: Dict[int, asyncio.Task] = {}

# ---------------- BUILD UI ----------------
def build_dashboard_text(user_id:int, name:str) -> str:
    u = get_user(user_id)
    role = u[2] if u else "member"
    status = u[3] if u else "free"
    limit = u[4] if u else 3
    txt = (
f"👋 Halo {name}\n"
"╭━━━〔 DASHBOARD 〕━━━╮\n"
f"• Bot Name : Nokos OTP Bot\n"
f"• Versi    : 1.0\n"
f"• Dev      : {DEV_USERNAME}\n"
"╰━━━━━━━━━━━━━━━━━━━╯\n\n"
"╭━━━〔 INFO AKUN 〕━━━╮\n"
f"• Nama     : {name}\n"
f"• Role     : {role}\n"
f"• Status   : {status}\n"
f"• Limit    : {limit if limit is not None else 'Unlimited'}\n"
"╰━━━━━━━━━━━━━━━━━━━╯\n\n"
"ℹ️ Fungsi Bot :\n"
"• 📱 Ambil Nomor (simulasi) untuk verifikasi (testing)\n"
"• 📜 Lihat Riwayat OTP yang masuk\n"
"• 🗑 Hapus nomor aktif\n"
"• 👨‍💻 Admin: kelola user & broadcast via tombol\n"
)
    return txt

def build_main_keyboard(is_admin:bool=False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("📱 Ambil Nomor", callback_data="get_number")],
        [InlineKeyboardButton("📜 Riwayat OTP", callback_data="list_otp"),
         InlineKeyboardButton("🗑 Hapus Nomor", callback_data="delete_number")],
        [InlineKeyboardButton("📋 Salin Nomor Aktif", callback_data="copy_active"),
         InlineKeyboardButton("👥 Undang Teman", callback_data="invite")],
        [InlineKeyboardButton("🛠 Tools", callback_data="tools"),
         InlineKeyboardButton("💎 Status", callback_data="status")],
    ]
    if is_admin:
        rows.append([InlineKeyboardButton("➕ Add Saldo", callback_data="admin_addsaldo"),
                     InlineKeyboardButton("💎 Set Premium", callback_data="admin_setpremium")])
        rows.append([InlineKeyboardButton("🚀 Broadcast", callback_data="admin_broadcast"),
                     InlineKeyboardButton("📋 Daftar User", callback_data="admin_users")])
    rows.append([InlineKeyboardButton("👨‍💻 Developer", callback_data="developer")])
    return InlineKeyboardMarkup(rows)

# ---------------- HANDLERS ----------------
# /start
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user.id, user.username or user.first_name)
    txt = build_dashboard_text(user.id, user.first_name)
    kb = build_main_keyboard(user.id == ADMIN_ID)
    try:
        # send photo with caption+keyboard (preferred)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=BANNER_URL, caption=txt, reply_markup=kb)
    except Exception:
        # fallback to text
        await update.message.reply_text(txt, reply_markup=kb)

# callback/tombol utama
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    ensure_user(user.id, user.username or user.first_name)
    is_admin = (user.id == ADMIN_ID)
    data = query.data

    # ------------- USER FLOWS -------------
    if data == "get_number":
        # show list of numbers from provider
        if query.message.photo:
            await query.edit_message_caption(caption="📱 Mencari nomor tersedia... Mohon tunggu.")
        else:
            await query.edit_message_text("📱 Mencari nomor tersedia... Mohon tunggu.")
        numbers = await provider.list_available_numbers()
        kb = [[InlineKeyboardButton(n, callback_data=f"choose:{n}")] for n in numbers]
        kb.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_home")])
        markup = InlineKeyboardMarkup(kb)
        if query.message.photo:
            await query.edit_message_caption(caption="Pilih nomor yang tersedia:", reply_markup=markup)
        else:
            await query.edit_message_text("Pilih nomor yang tersedia:", reply_markup=markup)
        return

    if data.startswith("choose:"):
        # user chose a number -> assign and start monitor
        number = data.split(":",1)[1]
        nid = add_number_for_user(user.id, number, "DummyProvider")
        async def on_msg_cb(text):
            add_message(nid, text)
            # send to user
            try:
                await context.bot.send_message(chat_id=user.id, text=f"🔑 OTP Masuk untuk {number}:\n\n{text}")
            except Exception:
                logger.exception("Gagal kirim OTP ke user.")
        task = await provider.start_monitor(number, lambda t: asyncio.create_task(on_msg_cb(t)))
        monitor_map[nid] = task
        out = f"✅ Nomor {number} aktif. Menunggu OTP masuk..."
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    if data == "list_otp":
        rows = list_messages_for_user(user.id)
        if not rows:
            out = "📜 Belum ada OTP / pesan untuk akun ini."
            if query.message.photo:
                await query.edit_message_caption(caption=out)
            else:
                await query.edit_message_text(out)
            return
        parts = []
        for text_msg, at, number in rows[:40]:
            parts.append(f"{number}\n{text_msg}\n— {at}")
        content = "\n\n".join(parts)
        if query.message.photo:
            await query.edit_message_caption(caption=f"📜 Riwayat pesan:\n\n{content}")
        else:
            await query.edit_message_text(f"📜 Riwayat pesan:\n\n{content}")
        return

    if data == "delete_number":
        active = get_active_number(user.id)
        if not active:
            out = "❌ Tidak ada nomor aktif."
            if query.message.photo:
                await query.edit_message_caption(caption=out)
            else:
                await query.edit_message_text(out)
            return
        nid, num, prov = active
        t = monitor_map.get(nid)
        if t:
            t.cancel()
        deactivate_number_by_id(nid)
        out = f"🗑 Nomor {num} berhasil dihapus."
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    if data == "copy_active":
        active = get_active_number(user.id)
        if not active:
            out = "❌ Tidak ada nomor aktif."
        else:
            _, num, _ = active
            out = f"🔖 Nomor aktif: {num}"
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    if data == "invite":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start={user.id}"
        out = f"👥 Bagikan link ini ke teman:\n{link}"
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    if data == "tools":
        kb = [
            [InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="back_home")],
            [InlineKeyboardButton("🔁 Ganti Provider (Admin only)", callback_data="switch_provider")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="back_home")],
        ]
        if query.message.photo:
            await query.edit_message_caption(caption="🛠 Tools Menu", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text("🛠 Tools Menu", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "status":
        u = get_user(user.id)
        out = f"💎 Status: {u[3]} | Limit: {u[4]}"
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    # ------------- ADMIN FLOWS (all via tombol + message input) -------------
    if data == "admin_users":
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        rows = list_users(60)
        if not rows:
            out = "Belum ada user."
            if query.message.photo:
                await query.edit_message_caption(caption=out)
            else:
                await query.edit_message_text(out)
            return
        # build keyboard paged (max 8 per page)
        kb = []
        for uid, uname, role, status, limit in rows[:40]:
            label = f"{uname or uid} | {status}"
            kb.append([InlineKeyboardButton(label, callback_data=f"admin_user_select:{uid}")])
        kb.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_home")])
        if query.message.photo:
            await query.edit_message_caption(caption="📋 Pilih user untuk lihat / kelola:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text("📋 Pilih user untuk lihat / kelola:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data.startswith("admin_user_select:"):
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        uid = int(data.split(":",1)[1])
        tu = get_user(uid)
        if not tu:
            await query.edit_message_text("User tidak ditemukan.")
            return
        _, uname, role, status, limit = tu
        out = f"🧾 User: {uname or uid}\nRole: {role}\nStatus: {status}\nLimit: {limit}"
        kb = [
            [InlineKeyboardButton("➕ Tambah Saldo (Top-up)", callback_data=f"admin_addsaldo_select:{uid}")],
            [InlineKeyboardButton("💎 Set Premium", callback_data=f"admin_setpremium_select:{uid}")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="admin_users")]
        ]
        if query.message.photo:
            await query.edit_message_caption(caption=out, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text(out, reply_markup=InlineKeyboardMarkup(kb))
        return

    # Admin add saldo: choose user -> then ask amount via message
    if data.startswith("admin_addsaldo_select:"):
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        target_id = int(data.split(":",1)[1])
        # set pending state in context.user_data
        context.user_data['pending_addsaldo'] = target_id
        prompt = f"Masukkan jumlah top-up untuk user {target_id} (kirim angka saja), atau tekan Batal."
        kb = [[InlineKeyboardButton("Batal", callback_data="admin_cancel")]]
        if query.message.photo:
            await query.edit_message_caption(caption=prompt, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "admin_cancel":
        # clear any pending states
        context.user_data.pop('pending_addsaldo', None)
        context.user_data.pop('pending_broadcast', None)
        out = "Operasi dibatalkan."
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    # Admin set premium select
    if data.startswith("admin_setpremium_select:"):
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        target_id = int(data.split(":",1)[1])
        set_user_status(target_id, "premium")
        out = f"✅ User {target_id} telah di-set ke PREMIUM."
        if query.message.photo:
            await query.edit_message_caption(caption=out)
        else:
            await query.edit_message_text(out)
        return

    # Admin broadcast entry: set pending flag then expect next message text as broadcast
    if data == "admin_broadcast":
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        context.user_data['pending_broadcast'] = True
        prompt = "🚀 Kirim pesan broadcast sekarang (balas pesan ini dengan teks yang ingin dikirim), atau tekan Batal."
        kb = [[InlineKeyboardButton("Batal", callback_data="admin_cancel")]]
        if query.message.photo:
            await query.edit_message_caption(caption=prompt, reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(kb))
        return

    # admin setpremium (top-level)
    if data == "admin_setpremium":
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        # show user list to select
        rows = list_users(100)
        kb = [[InlineKeyboardButton(f"{uname or uid} | {status}", callback_data=f"admin_setpremium_select:{uid}")] for uid, uname, _, status, _ in rows[:40]]
        kb.append([InlineKeyboardButton("🔙 Kembali", callback_data="back_home")])
        if query.message.photo:
            await query.edit_message_caption(caption="Pilih user untuk set premium:", reply_markup=InlineKeyboardMarkup(kb))
        else:
            await query.edit_message_text("Pilih user untuk set premium:", reply_markup=InlineKeyboardMarkup(kb))
        return

    # admin addsaldo root: show user list
    if data == "admin_addsaldo":
        if not is_admin:
            await query.answer("Hanya admin.", show_alert=True)
            return
        rows = list_users(100)
        kb = [[InlineKeyboardButton(f"{uname or uid} | {status}", callback_data=f"admin_addsaldo_select:{uid}")] for uid, uname, _, status,