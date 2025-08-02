#!/bin/bash

# ==================== THÔNG TIN CẤU HÌNH ====================
# Địa chỉ ví của bạn
WALLET_ADDRESS="43ZyyD81HJrhUaVYkfyV9A4pDG3AsyMmE8ATBZVQMLVW6FMszZbU28Wd35wWtcUZESeP3CAXW14cMAVYiKBtaoPCD5ZHPCj"
# Địa chỉ pool (SupportXMR.com với SSL/TLS)
POOL_ADDRESS="pool.supportxmr.com:443"
# Tên worker (tùy chọn)
WORKER_NAME="my_xmr_worker"
# Phiên bản XMRig mới nhất
XMRIG_VERSION="6.24.0"
# Đường dẫn tải xuống phiên bản static
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v$XMRIG_VERSION/xmrig-$XMRIG_VERSION-linux-static-x64.tar.gz"
# Thư mục cài đặt
INSTALL_DIR="$HOME/xmrig"

# =================== BẮT ĐẦU TỰ ĐỘNG HÓA ===================
echo "🚀 Bắt đầu quá trình thiết lập XMRig..."

# --- Bước 1: Cập nhật hệ thống và cài đặt các gói cần thiết ---
echo "⚙️ Cài đặt các công cụ cần thiết: wget, tar..."
sudo apt-get update > /dev/null 2>&1
sudo apt-get install -y wget tar > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Lỗi: Không thể cài đặt các gói cần thiết. Vui lòng kiểm tra lại quyền hoặc kết nối mạng."
    exit 1
fi

# --- Bước 2: Tạo thư mục và tải xuống XMRig ---
echo "📂 Tạo và chuyển đến thư mục $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || { echo "❌ Lỗi: Không thể tạo thư mục. Thoát."; exit 1; }

echo "📥 Tải xuống XMRig phiên bản $XMRIG_VERSION..."
wget "$XMRIG_URL" -O xmrig.tar.gz
if [ $? -ne 0 ]; then
    echo "❌ Lỗi: Không thể tải xuống XMRig. Vui lòng kiểm tra kết nối mạng hoặc đường dẫn."
    exit 1
fi

# --- Bước 3: Giải nén và dọn dẹp ---
echo "📦 Giải nén và thiết lập..."
tar -xzf xmrig.tar.gz
# mv xmrig-$XMRIG_VERSION/* . # Dòng này có thể không cần thiết với bản static
# rm -rf xmrig-$XMRIG_VERSION # Dòng này cũng vậy
rm -rf xmrig.tar.gz

# Cấp quyền thực thi cho XMRig
chmod +x xmrig

echo "✅ Thiết lập hoàn tất."

# --- Bước 4: Chạy XMRig và hiển thị log ---
echo "⛏️ Bắt đầu đào XMR... (Nhấn Ctrl+C để dừng)"
echo "Tỷ lệ sử dụng CPU sẽ là tối đa."

# Chạy XMRig với các tham số trên dòng lệnh
./xmrig --url "$POOL_ADDRESS" --user "$WALLET_ADDRESS.$WORKER_NAME" --pass "x" --tls
