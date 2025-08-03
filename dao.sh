
# ĐỊA CHỈ VÍ CỦA BẠN: Bắt buộc phải là địa chỉ ví Monero hợp lệ
WALLET_ADDRESS="43ZyyD81HJrhUaVYkfyV9A4pDG3AsyMmE8ATBZVQMLVW6FMszZbU28Wd35wWtcUZESeP3CAXW14cMAVYiKBtaoPCD5ZHPCj"
WORKER_NAME="my-gcp-miner"

# THÔNG TIN POOL: Cần chính xác, không thay đổi nếu không có nhu cầu
POOL_URL="pool.supportxmr.com:443"

# URL của phiên bản XMRig mới nhất dành cho Linux
XMRIG_URL="https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-x64.tar.gz"

# =========================================================
#       Các bước thực hiện
# =========================================================

echo "=========================================="
echo "      Script đào Monero trên Cloud Shell"
echo "=========================================="

# 1. Tải xuống và giải nén XMRig
echo "[1/3] Đang tải XMRig từ Github..."
curl -sL "$XMRIG_URL" | tar -zxvf -

# Di chuyển vào thư mục đã giải nén
cd xmrig-6.21.0

# 2. Chạy các lệnh tối ưu hóa hệ thống (có thể bị giới hạn)
# Tải module msr vào kernel và cấp quyền truy cập.
# Lưu ý: Các lệnh này có thể không thành công trên môi trường ảo hóa.
echo "[2/3] Đang cố gắng tải module msr và cấp quyền..."
sudo modprobe msr
sudo chmod 666 /dev/cpu/*/msr

# 3. Chạy XMRig với ưu tiên cao nhất
echo "[3/3] Bắt đầu đào Monero với ưu tiên cao nhất..."
echo "-----------------------------------------"

sudo ./xmrig -o "$POOL_URL" -u "$WALLET_ADDRESS" -p "$WORKER_NAME" --donate-level 1 -k --tls --priority=5

echo "-----------------------------------------"
echo "Script đã hoàn tất hoặc bị ngắt kết nối."
