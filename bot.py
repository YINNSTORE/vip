# nokos_full_bot.py (versi dengan OTP auto masuk)

import asyncio
import logging
import random
import sqlite3
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler,
    ContextTypes, MessageHandler, filters
)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8024500353:AAHg3SUbXKN6AcWpyow0JdR_3Xz0Z1DGZUE"
ADMIN_ID = 6353421952
DEV_USERNAME = "@yinnprovpn"
BANNER_URL = "https://awy.my.id/uploads/ini-linkfoto-baner.jpeg"
DB_FILE = "nokos_bot.db"

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

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role, status, limit_count FROM users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    conn.close()
    return r

def ensure_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if not get_user(user_id):
        role = "admin" if user_id == ADMIN_ID else "member"
        limit = None if role == "admin" else 3
        cur.execute("INSERT INTO users (user_id, username, role, status, limit_count) VALUES (?,?,?,?,?)",
                    (user_id, username, role, "free", limit))
        conn.commit()
    conn.close()

def update_user_limit(user_id, new_limit):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE users SET limit_count=? WHERE user_id=?", (new_limit, user_id))
    conn.commit()
    conn.close()

def set_user_status(user_id, status):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if status == "premium":
        cur.execute("UPDATE users SET status=?, limit_count=NULL WHERE user_id=?", (status, user_id))
    else:
        cur.execute("UPDATE users SET status=?, limit_count=? WHERE user_id=?", (status, 3, user_id))
    conn.commit()
    conn.close()

def list_all_users():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, status, limit_count FROM users ORDER BY rowid DESC LIMIT 20")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_number(user_id, number):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO numbers (user_id, number, active, created_at) VALUES (?,?,1,?)",
                (user_id, number, datetime.now().isoformat()))
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    return nid

def get_active_number(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, number FROM numbers WHERE user_id=? AND active=1", (user_id,))
    r = cur.fetchone()
    conn.close()
    return r

def deactivate_number(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE numbers SET active=0 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def save_message(number_id, text):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (number_id, text, received_at) VALUES (?,?,?)",
                (number_id, text, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def list_messages(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT m.text, m.received_at FROM messages m
        JOIN numbers n ON m.number_id=n.id
        WHERE n.user_id=? ORDER BY m.id DESC LIMIT 5
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- OTP PROVIDER SIMULASI ----------------
class DummyProvider:
    def __init__(self):
        self.pool = [f"+10000000{str(i).zfill(3)}" for i in range(1, 201)]
        self._tasks = {}

    async def list_numbers(self):
        await asyncio.sleep(0.05)
        return random.sample(self.pool, k=5)

    async def start_monitor(self, number_id, number, user_id, context: ContextTypes.DEFAULT_TYPE):
        async def sim_loop():
            while True:
                await asyncio.sleep(random.randint(10, 20))
                otp = f"{random.randint(100000, 999999)}"
                text = f"Kode OTP untuk {number}: {otp}"
                save_message(number_id, text)
                try:
                    await context.bot.send_message(chat_id=user_id, text=f"📩 OTP Masuk:\n{text}")
                except:
                    pass
        task = asyncio.create_task(sim_loop())
        self._tasks[user_id] = task
        return task

    def stop(self, user_id):
        t = self._tasks.get(user_id)
        if t:
            t.cancel()

provider = DummyProvider()

# ---------------- DASHBOARD ----------------
def build_dashboard(user_id, name):
    u = get_user(user_id)
    status = u[3] if u else "free"
    limit = u[4] if u else 3
    role = "admin" if user_id == ADMIN_ID else "member"
    return (
f"👋 Hai {name}\n"
"╭━━━〔 DASHBOARD 〕━━━╮\n"
"• Bot : Nokos OTP Bot\n"
f"• Dev : {DEV_USERNAME}\n"
"╰━━━━━━━━━━━━━━━━━━━╯\n\n"
"╭━━━〔 INFO AKUN 〕━━━╮\n"
f"• Status : {status}\n"
f"• Role   : {role}\n"
f"• Limit  : {limit if limit else 'Unlimited'}\n"
"╰━━━━━━━━━━━━━━━━━━━╯\n\n"
"ℹ️ Fungsi Bot:\n"
"• Ambil nomor dummy (simulasi)\n"
"• Terima OTP otomatis\n"
"• Admin bisa kelola user via tombol\n"
)

def build_keyboard(is_admin=False):
    rows = [
        [InlineKeyboardButton("📱 Ambil Nomor", callback_data="get_number")],
        [InlineKeyboardButton("📜 Riwayat OTP", callback_data="list_otp")],
        [InlineKeyboardButton("🗑 Hapus Nomor", callback_data="delete_number")],
        [InlineKeyboardButton("💎 Status", callback_data="status")]
    ]
    if is_admin:
        rows.append([
            InlineKeyboardButton("➕ Add Saldo", callback_data="admin_addsaldo"),
            InlineKeyboardButton("💎 Set Premium", callback_data="admin_setpremium")
        ])
        rows.append([
            InlineKeyboardButton("🚀 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton("📋 Daftar User", callback_data="admin_users")
        ])
    rows.append([InlineKeyboardButton("👨‍💻 Developer", callback_data="developer")])
    return InlineKeyboardMarkup(rows)

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user(user.id, user.username or user.first_name)
    text = build_dashboard(user.id, user.first_name)
    kb = build_keyboard(user.id == ADMIN_ID)
    try:
        await context.bot.send_photo(chat_id=user.id, photo=BANNER_URL, caption=text, reply_markup=kb)
    except Exception:
        await context.bot.send_message(chat_id=user.id, text=text, reply_markup=kb)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    ensure_user(user.id, user.username or user.first_name)

    # ---------- User ----------
    if q.data == "developer":
        await q.edit_message_caption(caption=f"👨‍💻 Developer: {DEV_USERNAME}")
        return

    if q.data == "status":
        u = get_user(user.id)
        msg = f"💎 Status kamu: {u[3]} | Limit: {u[4] if u[4] else 'Unlimited'}"
        await q.edit_message_caption(caption=msg)
        return

    if q.data == "get_number":
        # Cek user sudah punya nomor aktif?
        act = get_active_number(user.id)
        if act:
            await q.edit_message_caption(caption=f"⚠️ Kamu sudah punya nomor aktif: {act[1]}")
            return
        # Ambil nomor random dari pool
        numbers = await provider.list_numbers()
        pick = random.choice(numbers)
        nid = add_number(user.id, pick)
        await provider.start_monitor(nid, pick, user.id, context)
        await q.edit_message_caption(caption=f"✅ Nomor berhasil diambil:\n📱 {pick}\nOTP akan otomatis masuk di sini.")
        return

    if q.data == "delete_number":
        act = get_active_number(user.id)
        if not act:
            await q.edit_message_caption(caption="⚠️ Kamu tidak punya nomor aktif.")
            return
        deactivate_number(user.id)
        provider.stop(user.id)
        await q.edit_message_caption(caption=f"🗑 Nomor {act[1]} sudah dihapus.")
        return

    if q.data == "list_otp":
        msgs = list_messages(user.id)
        if not msgs:
            await q.edit_message_caption(caption="📭 Belum ada OTP yang masuk.")
            return
        lines = [f"{t} ({ts[:19]})" for t, ts in msgs]
        await q.edit_message_caption(caption="📜 Riwayat OTP:\n" + "\n".join(lines))
        return

    # ---------- Admin ----------
    if user.id == ADMIN_ID:
        if q.data == "admin_users":
            rows = list_all_users()
            msg = "📋 Daftar user:\n" + "\n".join([f"{uid} | {uname} | {status} | {limit}" for uid, uname, status, limit in rows])
            await q.edit_message_caption(caption=msg)
            return

        if q.data == "admin_addsaldo":
            rows = list_all_users()
            kb = []
            for uid, uname, status, limit in rows:
                kb.append([InlineKeyboardButton(f"{uname or uid} | {status}", callback_data=f"admin_addsaldo_select:{uid}")])
            await q.edit_message_caption(caption="📋 Pilih user untuk tambah saldo:", reply_markup=InlineKeyboardMarkup(kb))
            return

        if q.data.startswith("admin_addsaldo_select:"):
            target_id = int(q.data.split(":")[1])
            u = get_user(target_id)
            new_limit = (u[4] or 0) + 10
            update_user_limit(target_id, new_limit)
            await q.edit_message_caption(caption=f"✅ Saldo user {target_id} sudah ditambah 10. Total: {new_limit}")
            return

        if q.data == "admin_setpremium":
            rows = list_all_users()
            kb = []
            for uid, uname, status, limit in rows:
                kb.append([InlineKeyboardButton(f"{uname or uid} | {status}", callback_data=f"admin_setpremium_select:{uid}")])
            await q.edit_message_caption(caption="📋 Pilih user untuk set Premium:", reply_markup=InlineKeyboardMarkup(kb))
            return

        if q.data.startswith("admin_setpremium_select:"):
            target_id = int(q.data.split(":")[1])
            set_user_status(target_id, "premium")
            await q.edit_message_caption(caption=f"✅ User {target_id} sekarang Premium.")
            return

        if q.data == "admin_broadcast":
            context.user_data["await_broadcast"] = True
            await q.edit_message_caption(caption="🚀 Kirim teks broadcast (balas pesan ini).")
            return

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("await_broadcast") and update.effective_user.id == ADMIN_ID:
        text = update.message.text
        rows = list_all_users()
        for uid, _, _, _ in rows:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📣 {text}")
            except:
                pass
        context.user_data["await_broadcast"] = False
        await update.message.reply_text("✅ Broadcast terkirim.")

# ---------------- MAIN ----------------
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast))
    logger.info("Bot jalan...")
    app.run_polling()

if __name__ == "__main__":
    main()