const { makeWASocket, usePairingCode } = require("@whiskeysockets/baileys");
const axios = require("axios");
const dotenv = require("dotenv");
const readline = require("readline-sync");

dotenv.config();
const openaiApiKey = process.env.OPENAI_API_KEY;

async function startBot() {
    console.log("🚀 Bot WhatsApp ChatGPT siap dijalankan!");
    
    // Meminta nomor WhatsApp dari pengguna
    const phoneNumber = readline.question("Masukkan nomor WhatsApp Anda (contoh: 6281234567890): ");
    
    console.log("🔄 Menghasilkan Pairing Code...");
    const { state, saveCreds } = await usePairingCode(phoneNumber);
    
    const sock = makeWASocket({
        auth: state
    });

    sock.ev.on("creds.update", saveCreds);

    console.log("✅ Bot berhasil terhubung ke WhatsApp!");
    
    sock.ev.on("messages.upsert", async ({ messages }) => {
        const msg = messages[0];
        if (!msg.message || msg.key.fromMe) return;

        const sender = msg.key.remoteJid;
        const text = msg.message.conversation || msg.message.extendedTextMessage?.text;

        console.log(`📩 Pesan dari ${sender}: ${text}`);

        if (text) {
            const response = await getChatGPTResponse(text);
            await sock.sendMessage(sender, { text: response });
        }
    });

    async function getChatGPTResponse(prompt) {
        try {
            const res = await axios.post(
                "https://api.openai.com/v1/chat/completions",
                {
                    model: "gpt-4",
                    messages: [{ role: "user", content: prompt }]
                },
                { headers: { Authorization: `Bearer ${openaiApiKey}`, "Content-Type": "application/json" } }
            );

            return res.data.choices[0].message.content.trim();
        } catch (err) {
            console.error("❌ Error OpenAI:", err.response?.data || err.message);
            return "Maaf, terjadi kesalahan dalam memproses permintaan.";
        }
    }
}

startBot();
