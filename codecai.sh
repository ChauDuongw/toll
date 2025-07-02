#!/bin/bash

# --- CẤU HÌNH CỦA BẠN ---
MONERO_WALLET_ADDRESS="85JiygdevZmb1AxUosPHyxC13iVu9zCydQ2mDFEBJaHp2wyupPnq57n6bRcNBwYSh9bA5SA4MhTDh9moj55FwinXGn9jDkz"
POOL_URL="pool.hashvault.pro:443"
WORKER_NAME="my_user_miner_no_sudo_XMR"
CPU_THREADS="" # XMRig sẽ tự động phát hiện số luồng tốt nhất nếu để trống

# --- KHÔNG CẦN CHỈNH SỬA TỪ ĐÂY TRỞ XUỐNG NẾU BẠN KHÔNG CHẮC CHẮN ---

XMRIG_DIR="xmrig_miner"
XMRIG_VERSION="6.24.0"
# Tên tệp TAR.GZ mà bạn đã TẢI XUỐNG THỦ CÔNG và đặt cùng thư mục với script này
XMRIG_TAR_FILE="xmrig-${XMRIG_VERSION}-linux-x64.tar.gz"

# Hàm kiểm tra lỗi và thoát
check_error() {
    if [ $? -ne 0 ]; then
        echo "LỖI: $1"
        exit 1
    fi
}

echo "--- Bắt đầu Script chạy XMRig Miner (KHÔNG CẦN SUDO) ---"
echo "LƯU Ý: Hiệu suất đào có thể thấp hơn do không có quyền tối ưu hóa hệ thống."
echo "==================================================="

# 1. Giải nén XMRig
echo "Đang kiểm tra và giải nén XMRig..."
if [ ! -f "$XMRIG_TAR_FILE" ]; then
    echo "LỖI: Không tìm thấy tệp '$XMRIG_TAR_FILE' trong thư mục hiện tại."
    echo "Vui lòng tải xuống thủ công từ https://github.com/xmrig/xmrig/releases/download/v${XMRIG_VERSION}/xmrig-${XMRIG_VERSION}-linux-x64.tar.gz"
    echo "và đặt nó vào cùng thư mục với script này."
    exit 1
fi

if [ ! -d "$XMRIG_DIR" ]; then
    mkdir "$XMRIG_DIR"
fi

tar -xzvf "$XMRIG_TAR_FILE" -C "$XMRIG_DIR" --strip-components=1 >/dev/null 2>&1
check_error "Không thể giải nén XMRig. Tệp .tar.gz có thể bị hỏng hoặc không phải định dạng tar.gz hợp lệ."
echo "Đã giải nén XMRig thành công."
echo "---------------------------------------------------"

# 2. Cấp quyền thực thi XMRig
echo "Đang cấp quyền thực thi cho XMRig..."
if [ ! -x "$XMRIG_DIR/xmrig" ]; then
    chmod +x "$XMRIG_DIR/xmrig"
fi
echo "Đã cấp quyền thực thi cho XMRig thành công."
echo "---------------------------------------------------"

# 3. Chạy XMRig Miner
echo "--- Đang khởi chạy XMRig Miner ---"
echo "Bạn sẽ thấy log của miner bên dưới. Để dừng, nhấn Ctrl+C."
echo "==================================================="

# Chuyển vào thư mục XMRig để chạy miner
cd "$XMRIG_DIR" || check_error "Không thể vào thư mục XMRig."

# Chạy miner với các tham số bạn đã cấu hình
# XMRig sẽ tự động hiển thị log ra terminal
if [ -n "$CPU_THREADS" ]; then
    ./xmrig -a rx/0 -o "$POOL_URL" -u "$MONERO_WALLET_ADDRESS" -p "$WORKER_NAME" --cpu-max-threads="$CPU_THREADS"
else
    ./xmrig -a rx/0 -o "$POOL_URL" -u "$MONERO_WALLET_ADDRESS" -p "$WORKER_NAME"
fi

# Lệnh này chỉ chạy sau khi XMRig dừng (bạn nhấn Ctrl+C)
echo "==================================================="
echo "--- XMRig Miner đã dừng. ---"
