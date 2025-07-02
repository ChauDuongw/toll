#!/bin/bash

echo "--- Bắt đầu Script cài đặt và chạy XMRig Miner ---"
echo "Bạn có thể được yêu cầu nhập mật khẩu sudo để cài đặt các phụ thuộc hệ thống."
echo "==================================================="

# --- CẤU HÌNH CỦA BẠN (HÃY CHẮN CHẮN ĐÂY LÀ THÔNG TIN CHÍNH XÁC CỦA BẠN) ---
MONERO_WALLET_ADDRESS="85JiygdevZmb1AxUosPHyxC13iVu9zCydQ2mDFEBJaHp2wyupPnq57n6bRcNBwYSh9bA5SA4MhTDh9moj55FwinXGn9jDkz"
POOL_URL="pool.hashvault.pro:443"
WORKER_NAME="my_ubuntu_miner_XMR"
CPU_THREADS=""

# --- KHÔNG CẦN CHỈNH SỬA TỪ ĐÂY TRỞ XUỐNG NẾU BẠN KHÔNG CHẮC CHẮN ---

XMRIG_DIR="xmrig_miner"
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v6.21.3/xmrig-6.21.3-linux-x64.tar.gz"
XMRIG_TAR_FILE="xmrig-6.21.3-linux-x64.tar.gz"

# 1. Cập nhật hệ thống và cài đặt các gói cần thiết
echo "Đang cài đặt các phụ thuộc hệ thống..."
sudo apt update >/dev/null 2>&1
sudo apt install -y build-essential libhwloc-dev libssl-dev git screen wget tar >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể cài đặt các phụ thuộc hệ thống. Vui lòng kiểm tra kết nối internet hoặc quyền sudo."
    exit 1
fi
echo "Đã cài đặt thành công các phụ thuộc hệ thống."
echo "---------------------------------------------------"

# 2. Cấu hình MSR và Huge Pages để tối ưu Hashrate
echo "Đang cấu hình MSR và Huge Pages để tối ưu hiệu suất đào..."

# Cấu hình MSR (Model-Specific Register)
echo "   - Cấu hình MSR..."
if ! grep -q "msr" /etc/modules; then
    echo "msr" | sudo tee -a /etc/modules > /dev/null
fi
sudo modprobe msr >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   Cảnh báo: Không thể tải module MSR. Hashrate có thể thấp. Đảm bảo 'msr-tools' đã được cài đặt (nếu cần) và bạn có quyền."
fi

# Cấu hình Huge Pages (trang bộ nhớ lớn)
echo "   - Cấu hình Huge Pages..."
HUGEPAGES_COUNT=1280 
sudo sysctl -w vm.nr_hugepages=$HUGEPAGES_COUNT >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   Cảnh báo: Không thể cấu hình Huge Pages. Hashrate có thể thấp. Đảm bảo bạn có đủ RAM trống."
fi

# Để cấu hình Huge Pages tồn tại vĩnh viễn (sau khi khởi động lại)
if ! grep -q "vm.nr_hugepages=$HUGEPAGES_COUNT" /etc/sysctl.conf; then
    echo "vm.nr_hugepages=$HUGEPAGES_COUNT" | sudo tee -a /etc/sysctl.conf > /dev/null
    echo "   (Cấu hình Huge Pages đã được thêm vào /etc/sysctl.conf để duy trì sau khởi động lại)"
fi

# Kiểm tra và mount hugetlbfs (nếu cần)
if ! mountpoint -q /mnt/huge; then
    echo "   - Đang mount hugetlbfs..."
    sudo mkdir -p /mnt/huge >/dev/null 2>&1
    sudo mount -t hugetlbfs none /mnt/huge >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "   Cảnh báo: Không thể mount hugetlbfs. Hashrate có thể thấp."
    fi
fi

# Đảm bảo người dùng hiện tại có quyền truy cập huge pages
USERNAME=$(whoami)
if ! groups $USERNAME | grep -q "hugetlbfs"; then
    echo "   - Thêm người dùng '$USERNAME' vào nhóm 'hugetlbfs'..."
    sudo groupadd -f hugetlbfs >/dev/null 2>&1
    sudo usermod -aG hugetlbfs $USERNAME >/dev/null 2>&1
    echo "   Bạn có thể cần đăng xuất và đăng nhập lại để thay đổi nhóm có hiệu lực đầy đủ."
fi

echo "Đã cấu hình thành công hệ thống để tối ưu hiệu suất."
echo "---------------------------------------------------"

# 3. Tải xuống và giải nén XMRig
echo "Đang tải xuống và giải nén XMRig..."
if [ ! -d "$XMRIG_DIR" ]; then
    mkdir "$XMRIG_DIR"
fi

wget -q --show-progress "$XMRIG_URL" -O "$XMRIG_TAR_FILE" >/dev/null 2>&1 # Dòng này vẫn giữ show-progress
if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể tải xuống XMRig. Vui lòng kiểm tra URL hoặc kết nối internet."
    exit 1
fi

echo "Đã tải xuống XMRig thành công."
echo "Đang giải nén XMRig..."
tar -xzvf "$XMRIG_TAR_FILE" -C "$XMRIG_DIR" --strip-components=1 >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể giải nén XMRig. Vui lòng kiểm tra tệp .tar.gz."
    exit 1
fi
echo "Đã giải nén XMRig thành công."

# Dọn dẹp file tar
rm "$XMRIG_TAR_FILE" >/dev/null 2>&1
echo "---------------------------------------------------"

# 4. Kiểm tra quyền thực thi XMRig
echo "Đang kiểm tra và cấp quyền thực thi cho XMRig..."
if [ ! -x "$XMRIG_DIR/xmrig" ]; then
    chmod +x "$XMRIG_DIR/xmrig"
fi
echo "Đã cấp quyền thực thi cho XMRig thành công."
echo "---------------------------------------------------"

# 5. Chạy XMRig Miner
echo "--- Đang khởi chạy XMRig Miner ---"
echo "Bạn sẽ thấy log của miner bên dưới. Để dừng, nhấn Ctrl+C."
echo "==================================================="

# Chuyển vào thư mục XMRig để chạy miner
cd "$XMRIG_DIR" || { echo "Lỗi: Không thể vào thư mục XMRig."; exit 1; }

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
echo "Bạn có thể chạy lại script này bất cứ lúc nào, hoặc chạy trực tiếp './xmrig_miner/xmrig -a rx/0 -o $POOL_URL -u $MONERO_WALLET_ADDRESS -p $WORKER_NAME' từ terminal."
