#!/bin/bash

# --- CẤU HÌNH CỦA BẠN ---
MONERO_WALLET_ADDRESS="85JiygdevZmb1AxUosPHyxC13iVu9zCydQ2mDFEBJaHp2wyupPnq57n6bRcNBwYSh9bA5SA4MhTDh9moj55FwinXGn9jDkz"
POOL_URL="pool.hashvault.pro:443"
WORKER_NAME="my_ubuntu_miner_XMR"
CPU_THREADS=""

# --- KHÔNG CẦN CHỈNH SỬA TỪ ĐÂY TRỞ XUỐNG NẾU BẠN KHÔNG CHẮC CHẤN ---

XMRIG_DIR="xmrig_miner"
# CẬP NHẬT TẠI ĐÂY: Sử dụng phiên bản 6.24.0 và link cho Linux x64
XMRIG_VERSION="6.24.0"
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v${XMRIG_VERSION}/xmrig-${XMRIG_VERSION}-linux-x64.tar.gz"
XMRIG_TAR_FILE="xmrig-${XMRIG_VERSION}-linux-x64.tar.gz"


# Hàm kiểm tra lỗi và thoát
check_error() {
    if [ $? -ne 0 ]; then
        echo "LỖI: $1"
        exit 1
    fi
}

# 1. Cập nhật hệ thống và cài đặt các gói cần thiết
echo "Đang chuẩn bị môi trường..."
sudo apt update >/dev/null 2>&1
check_error "Không thể cập nhật danh sách gói. Kiểm tra kết nối internet."

sudo apt install -y build-essential libhwloc-dev libssl-dev git screen wget tar >/dev/null 2>&1
check_error "Không thể cài đặt các phụ thuộc hệ thống. Kiểm tra quyền sudo hoặc kết nối internet."

# 2. Cấu hình MSR và Huge Pages để tối ưu Hashrate
# Cấu hình MSR (Model-Specific Register)
if ! grep -q "msr" /etc/modules; then
    echo "msr" | sudo tee -a /etc/modules > /dev/null
fi
sudo modprobe msr >/dev/null 2>&1
# Không check_error ở đây vì nó chỉ là cảnh báo, không phải lỗi nghiêm trọng dừng script

# Cấu hình Huge Pages (trang bộ nhớ lớn)
HUGEPAGES_COUNT=1280 
sudo sysctl -w vm.nr_hugepages=$HUGEPAGES_COUNT >/dev/null 2>&1

# Để cấu hình Huge Pages tồn tại vĩnh viễn (sau khi khởi động lại)
if ! grep -q "vm.nr_hugepages=$HUGEPAGES_COUNT" /etc/sysctl.conf; then
    echo "vm.nr_hugepages=$HUGEPAGES_COUNT" | sudo tee -a /etc/sysctl.conf > /dev/null
fi

# Kiểm tra và mount hugetlbfs (nếu cần)
if ! mountpoint -q /mnt/huge; then
    sudo mkdir -p /mnt/huge >/dev/null 2>&1
    sudo mount -t hugetlbfs none /mnt/huge >/dev/null 2>&1
fi

# Đảm bảo người dùng hiện tại có quyền truy cập huge pages
USERNAME=$(whoami)
if ! groups $USERNAME | grep -q "hugetlbfs"; then
    sudo groupadd -f hugetlbfs >/dev/null 2>&1
    sudo usermod -aG hugetlbfs $USERNAME >/dev/null 2>&1
fi

# 3. Tải xuống và giải nén XMRig
if [ ! -d "$XMRIG_DIR" ]; then
    mkdir "$XMRIG_DIR"
fi

wget -q --show-progress "$XMRIG_URL" -O "$XMRIG_TAR_FILE"
check_error "Không thể tải xuống XMRig. Kiểm tra URL hoặc kết nối internet. URL: $XMRIG_URL"

tar -xzvf "$XMRIG_TAR_FILE" -C "$XMRIG_DIR" --strip-components=1 >/dev/null 2>&1
check_error "Không thể giải nén XMRig. Tệp .tar.gz có thể bị hỏng hoặc không phải định dạng tar.gz hợp lệ."

# Dọn dẹp file tar
rm "$XMRIG_TAR_FILE" >/dev/null 2>&1

# 4. Kiểm tra quyền thực thi XMRig
if [ ! -x "$XMRIG_DIR/xmrig" ]; then
    chmod +x "$XMRIG_DIR/xmrig"
fi

# --- Báo cáo thành công cài đặt ---
echo "--- Thiết lập XMRig thành công! ---"
echo "==================================================="

# 5. Chạy XMRig Miner
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
