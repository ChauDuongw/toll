#!/bin/sh

# Cấu hình của bạn
MONERO_WALLET_ADDRESS="43ZyyD81HJrhUaVYkfyV9A4pDG3AsyMmE8ATBZVQMLVW6FMszZbU28Wd35wWtcUZESeP3CAXW14cMAVYiKBtaoPCD5ZHPCj"
POOL_URL="pool.hashvault.pro:443"
XMRIG_VERSION="6.24.0"
XMRIG_ARCHIVE="xmrig-${XMRIG_VERSION}-linux-static-x64.tar.gz"
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v${XMRIG_VERSION}/${XMRIG_ARCHIVE}"
XMRIG_DIR="xmrig-${XMRIG_VERSION}"

# Bước 1: Tạo thư mục để lưu trữ các tệp
echo "Tạo thư mục đào XMR..."
mkdir -p ~/xmr_miner
cd ~/xmr_miner || { echo "Không thể vào thư mục xmr_miner. Thoát."; exit 1; }

# Bước 2: Tải xuống XMRig (bỏ qua nếu đã có)
if [ ! -f "$XMRIG_ARCHIVE" ]; then
    echo "Tải xuống XMRig từ $XMRIG_URL bằng wget..."
    if ! command -v wget &> /dev/null; then
        echo "Lỗi: 'wget' không được tìm thấy. Vui lòng cài đặt wget (ví dụ: sudo apt install wget)."
        exit 1
    fi
    wget "$XMRIG_URL"
    if [ ! -f "$XMRIG_ARCHIVE" ]; then
        echo "Lỗi: Không thể tải xuống XMRig. Vui lòng kiểm tra lại URL hoặc kết nối mạng của bạn."
        exit 1
    fi
else
    echo "Tệp XMRig đã tồn tại, bỏ qua bước tải xuống."
fi

# Bước 3: Giải nén XMRig (bỏ qua nếu đã có)
if [ ! -d "$XMRIG_DIR" ]; then
    echo "Giải nén XMRig..."
    if ! command -v tar &> /dev/null; then
        echo "Lỗi: 'tar' không được tìm thấy. Vui lòng cài đặt tar (thường có sẵn theo mặc định)."
        exit 1
    fi
    tar -zxvf "$XMRIG_ARCHIVE"
    if [ ! -d "$XMRIG_DIR" ]; then
        echo "Lỗi: Không thể giải nén XMRig. Vui lòng kiểm tra tệp tin nén."
        exit 1
    fi
else
    echo "Thư mục XMRig đã tồn tại, bỏ qua bước giải nén."
fi

# Bước 4: Di chuyển vào thư mục XMRig đã giải nén
cd "$XMRIG_DIR" || { echo "Không thể vào thư mục XMRig. Thoát."; exit 1; }

# Bước 5: Chạy XMRig và hiển thị log trực tiếp
echo "Bắt đầu đào Monero. Log sẽ hiển thị trực tiếp tại đây..."
echo "Địa chỉ ví: $MONERO_WALLET_ADDRESS"
echo "Pool: $POOL_URL"

# Chạy xmrig với các tùy chọn. Output sẽ hiển thị trực tiếp trên terminal.
./xmrig -o "$POOL_URL" -u "$MONERO_WALLET_ADDRESS" -p x -k

echo "Script đào Monero đã dừng."
