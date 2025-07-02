#!/bin/bash

echo "--- Script cài đặt và chạy XMRig Miner ---"
echo "Đây là script dành cho hệ điều hành Linux (Debian/Ubuntu)."
echo "Bạn có thể được yêu cầu nhập mật khẩu sudo để cài đặt các phụ thuộc hệ thống."

# --- CẤU HÌNH CỦA BẠN ---
# Địa chỉ ví Monero của bạn. THAY THẾ CHỖ NÀY BẰNG ĐỊA CHỈ VÍ THẬT CỦA BẠN!
MONERO_WALLET_ADDRESS="85JiygdevZmb1AxUosPHyxC13iVu9zCydQ2mDFEBJaHp2wyupPnq57n6bRcNBwYSh9bA5SA4MhTDh9moj55FwinXGn9jDkz"

# URL của Pool đào. Thay đổi nếu bạn muốn sử dụng pool khác.
# Ví dụ: pool.hashvault.pro:443, xmr.2miners.com:2222, de.minexmr.com:443
POOL_URL="pool.hashvault.pro:443"

# Tên worker (tùy chọn). Đặt tên bất kỳ để dễ quản lý trên pool.
WORKER_NAME="my_ubuntu_miner" # Bạn có thể thay đổi tên này nếu muốn

# Cấu hình CPU threads (số luồng CPU mà miner sẽ sử dụng).
# Nên để bằng số lõi vật lý của CPU của bạn (hoặc số luồng hợp lý).
# Để trống hoặc 0 để XMRig tự động phát hiện (thường là tốt nhất).
CPU_THREADS="" # Ví dụ: "8" để sử dụng 8 luồng, hoặc để trống "" để tự động

# --- KHÔNG CẦN CHỈNH SỬA TỪ ĐÂY TRỞ XUỐNG NẾU BẠN KHÔNG CHẮC CHẮN ---

XMRIG_DIR="xmrig_miner"
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v6.21.3/xmrig-6.21.3-linux-x64.tar.gz"
XMRIG_TAR_FILE="xmrig-6.21.3-linux-x64.tar.gz"

# Phần còn lại của script vẫn giữ nguyên như tôi đã cung cấp trước đó.
# ... (các bước cài đặt phụ thuộc, cấu hình MSR, Huge Pages, tải xuống XMRig, chạy miner)
