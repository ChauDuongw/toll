#!/bin/bash

# Thông tin tài khoản
WALLET_ADDRESS="43ZyyD81HJrhUaVYkfyV9A4pDG3AsyMmE8ATBZVQMLVW6FMszZbU28Wd35wWtcUZESeP3CAXW14cMAVYiKBtaoPCD5ZHPCj"
WORKER_NAME="my-colab-miner"

# Thông tin Pool mới
POOL_URL="pool.supportxmr.com:443"

# URL của phiên bản XMRig mới nhất dành cho Linux 64-bit
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-x64.tar.gz"

# Bắt đầu script
echo "Đang tải XMRig từ Github..."
curl -sL "$XMRIG_URL" -o xmrig.tar.gz

echo "Đang giải nén file..."
tar -zxvf xmrig.tar.gz

# Di chuyển vào thư mục đã giải nén
cd xmrig-6.21.0

# Chạy XMRig với các thông số
echo "Bắt đầu đào Monero với pool mới..."
./xmrig -o "$POOL_URL" -u "$WALLET_ADDRESS" -p "$WORKER_NAME" --donate-level 1 -k --tls
