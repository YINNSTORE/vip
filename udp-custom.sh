#!/bin/bash
clear
cd
rm -rf /etc/udp
mkdir -p /etc/udp
echo "change to time GMT+7"
ln -fs /usr/share/zoneinfo/Asia/Jakarta /etc/localtime
cd /etc/udp
wget -q -O udp-custom "https://github.com/zhets/udp-custom/raw/main/udp-custom-linux-amd64"
chmod +x udp-custom
cd

cat <<EOF > /etc/udp/config.json
{
  "listen": ":36712",
  "stream_buffer": 33554432,
  "receive_buffer": 83886080,
  "auth": {
    "mode": "passwords"
  }
}
EOF

chmod 644 /etc/udp/config.json

if [ -z "$1" ]; then
cat <<EOF > /etc/systemd/system/udp-custom.service
[Unit]
Description=UDP Custom by ePro Dev. Team

[Service]
User=root
Type=simple
ExecStart=/etc/udp/udp-custom server
WorkingDirectory=/etc/udp/
Restart=always
RestartSec=2s

[Install]
WantedBy=default.target
EOF
else
cat <<EOF > /etc/systemd/system/udp-custom.service
[Unit]
Description=UDP Custom by ePro Dev. Team

[Service]
User=root
Type=simple
ExecStart=/etc/udp/udp-custom server -exclude $1
WorkingDirectory=/etc/udp/
Restart=always
RestartSec=2s

[Install]
WantedBy=default.target
EOF
fi

systemctl start udp-custom &>/dev/null
systemctl enable udp-custom &>/dev/null
systemctl restart udp-custom &>/dev/null

echo " Install udp success "
sleep 2 
clear