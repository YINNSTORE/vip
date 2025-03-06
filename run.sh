#!/bin/bash
# ====================================================
# Script Rebuild VPS DigitalOcean - Made by Yinn
# Jangan Ubah Kalo Kembangin Boleh, Dan Jangan Hapus Nama Credit Pembuat
# ====================================================

# API DigitalOcean (Ganti Sama Token Lu)
DIGITALOCEAN_API_TOKEN="apikey_digitalocean_punyalu"
API_BASE_URL="https://api.digitalocean.com/v2"

# Konfigurasi Bot Telegram (Ganti Sama Bot Lu)
TELEGRAM_BOT_TOKEN="7667938486:AAGf1jtnAj__TwNUQhm7nzzncFyD0zw92vg"
TELEGRAM_CHAT_ID="6353421952"

clear

while true; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🧿 MENU UTAMA 🧿"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "1) Rebuild VPS"
    echo "2) Lihat Daftar VPS"
    echo "3) Keluar"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -p "⏩ Pilih menu: " menu_choice

    case $menu_choice in
        1)
            clear
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "🔹 REBUILD VPS 🔹"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

            read -p "⏩ Masukkan IP VPS: " VPS_IP

            # Cek VPS berdasarkan IP
            DROPLET_RESPONSE=$(curl -s -X GET "$API_BASE_URL/droplets" -H "Authorization: Bearer $DIGITALOCEAN_API_TOKEN")
            VPS_DROPLET_ID=$(echo "$DROPLET_RESPONSE" | jq -r --arg VPS_IP "$VPS_IP" '.droplets[] | select(.networks.v4[].ip_address==$VPS_IP) | .id')
            NAMA_DROPLET=$(echo "$DROPLET_RESPONSE" | jq -r --arg VPS_IP "$VPS_IP" '.droplets[] | select(.networks.v4[].ip_address==$VPS_IP) | .name')
            OS_LAMA=$(echo "$DROPLET_RESPONSE" | jq -r --arg VPS_IP "$VPS_IP" '.droplets[] | select(.networks.v4[].ip_address==$VPS_IP) | .image.slug')

            if [[ -z "$VPS_DROPLET_ID" ]]; then
                echo "❌ VPS dengan IP $VPS_IP gak ditemukan!"
                exit 1
            fi

            echo "🔹 Pilih OS Rebuild:"
            echo "1) Ubuntu 18.04"
            echo "2) Ubuntu 20.04"
            echo "3) Ubuntu 22.04"
            echo "4) Ubuntu 24.04"
            echo "5) Debian 11"
            echo "6) Debian 12"
            echo "7) Batal"
            read -p "⏩ Pilih OS (1-7): " os_choice

            case $os_choice in
                1) OS_BARU="ubuntu-18-04-x64" ;;
                2) OS_BARU="ubuntu-20-04-x64" ;;
                3) OS_BARU="ubuntu-22-04-x64" ;;
                4) OS_BARU="ubuntu-24-04-x64" ;;
                5) OS_BARU="debian-11-x64" ;;
                6) OS_BARU="debian-12-x64" ;;
                7) echo "❌ Batal!"; exit 1 ;;
                *) echo "❌ Pilihan gak valid!"; exit 1 ;;
            esac

            # Konfirmasi rebuild
            read -p "⚠️ Rebuild VPS dengan OS $OS_BARU. Lanjut? (y/n): " confirm
            if [[ "$confirm" != "y" ]]; then exit 1; fi

            # Kirim notifikasi ke Telegram sebelum rebuild
            curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
                -d "chat_id=$TELEGRAM_CHAT_ID" \
                -d "text=━━━━━━━━━━━━━━━━━━━━
🧿 *NOTIFIKASI REBUILD* 🧿
━━━━━━━━━━━━━━━━━━━━
📌 *NAMA DROPLET:* $NAMA_DROPLET
🌍 *IP VPS:* $VPS_IP
🔄 *OS Lama:* ${OS_LAMA:-Tidak Diketahui}
💿 *OS Baru:* $OS_BARU
⏳ *Status:* *Sedang Diproses...*
━━━━━━━━━━━━━━━━━━━━" \
                -d "parse_mode=Markdown"

            # Mulai rebuild VPS
            echo "⚡ Mulai rebuild VPS ($OS_BARU)..."
            RESPONSE=$(curl -s -X POST "$API_BASE_URL/droplets/$VPS_DROPLET_ID/actions" \
                -H "Authorization: Bearer $DIGITALOCEAN_API_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{"type":"rebuild","image":"'"$OS_BARU"'"}')

            if echo "$RESPONSE" | grep -q "action"; then
                echo "✅ VPS sedang diproses. Tunggu beberapa menit..."
            else
                echo "❌ Gagal rebuild VPS!"
                exit 1
            fi

            # Tunggu 2 Menit
            sleep 120

            # Ambil Tanggal & Jam Sekarang
            TANGGAL=$(date "+%Y-%m-%d")
            JAM=$(date "+%H:%M:%S")

            # Kirim notifikasi ke Telegram setelah rebuild sukses
            curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
                -d "chat_id=$TELEGRAM_CHAT_ID" \
                -d "text=━━━━━━━━━━━━━━━━━━━━
🧿 *NOTIFIKASI REBUILD* 🧿
━━━━━━━━━━━━━━━━━━━━
📌 *NAMA DROPLET:* $NAMA_DROPLET
🌍 *IP VPS:* $VPS_IP
🔄 *OS Lama:* ${OS_LAMA:-Tidak Diketahui}
💿 *OS Baru:* $OS_BARU
📅 *Tanggal:* $TANGGAL
⏰ *Jam:* $JAM
🟢 *Status:* *Sukses!*
━━━━━━━━━━━━━━━━━━━━" \
                -d "parse_mode=Markdown"

            echo "✅ Rebuild selesai!"
            ;;
        2)
            echo "🔍 Ambil daftar VPS..."
            ;;
        3)
            echo "❌ Keluar dari script."
            exit 0
            ;;
        *)
            echo "❌ Pilihan gak valid! Coba lagi."
            ;;
    esac
done

# Credit By Yinn
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔹 Script Rebuild VPS by Yinn 🔹"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"