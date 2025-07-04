#!/bin/bash

# Địa chỉ ví của bạn
WALLET_ADDRESS="43ZyyD81HJrhUaVYkfyV9A4pDG3AsyMmE8ATBZVQMLVW6FMszZbU28Wd35wWtcUZESeP3CAXW14cMAVYiKBtaoPCD5ZHPCj"
# Địa chỉ pool - SupportXMR.com với cổng 443 (SSL/TLS)
POOL_ADDRESS="pool.supportxmr.com:443"

# Tên worker (tùy chọn, bạn có thể thay đổi để dễ quản lý)
WORKER_NAME="my_xmr_worker"
# Phiên bản XMRig để tải xuống
XMRIG_VERSION="6.21.0"
# Đường dẫn cài đặt (thư mục home của bạn)
INSTALL_DIR="$HOME/xmrig"
# Tên file log
LOG_FILE="xmrig_mining.log"

# --- Bắt đầu tập lệnh ---

echo "Bắt đầu thiết lập và cấu hình XMRig..."

# Tạo thư mục cài đặt nếu chưa có
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || { echo "Không thể chuyển đến thư mục $INSTALL_DIR. Thoát."; exit 1; }

# Kiểm tra xem XMRig đã được tải xuống chưa
if [ ! -f "xmrig" ]; then
    echo "Tải xuống XMRig phiên bản $XMRIG_VERSION..."
    # Lấy phiên bản XMRig cho Linux x64
    wget "https://github.com/xmrig/xmrig/releases/download/v$XMRIG_VERSION/xmrig-$XMRIG_VERSION-linux-x64.tar.gz" -O xmrig.tar.gz
    if [ $? -ne 0 ]; then
        echo "Lỗi khi tải xuống XMRig. Vui lòng kiểm tra kết nối mạng hoặc phiên bản."
        exit 1
    fi

    tar -xzf xmrig.tar.gz
    # Di chuyển file xmrig từ thư mục giải nén ra thư mục gốc để dễ chạy
    mv xmrig-$XMRIG_VERSION/* .
    rm -rf xmrig-$XMRIG_VERSION xmrig.tar.gz

    echo "XMRig đã được tải xuống và giải nén."
else
    echo "XMRig đã tồn tại. Bỏ qua bước tải xuống."
fi

# Cấp quyền thực thi cho XMRig
chmod +x xmrig

# Tạo file cấu hình config.json
echo "Tạo file cấu hình config.json..."
cat << EOF > config.json
{
    "autosave": true,
    "cpu": true,
    "opencl": false,
    "cuda": false,
    "pools": [
        {
            "algo": null,
            "coin": null,
            "url": "$POOL_ADDRESS",
            "user": "$WALLET_ADDRESS.$WORKER_NAME",
            "pass": "x",
            "rig-id": null,
            "nicehash": false,
            "keepalive": true,
            "tls": true,
            "daemon": false,
            "socks5": null,
            "self-select": null,
            "motp": null,
            "log-on-success": true,
            "log-on-error": true,
            "dns-over-https": null,
            "dns-fallback": [],
            "bind": null,
            "usage-report": false,
            "syslog": false,
            "tls-fingerprint": null
        }
    ],
    "print-time": 60,
    "api": {
        "id": null,
        "host": "127.0.0.1",
        "port": 0,
        "access-token": null,
        "ipv6": false,
        "restricted": true
    },
    "donate-level": 1,
    "user-agent": null,
    "syslog": false,
    "log-file": "$LOG_FILE",
    "log-level": 2,
    "background": false,
    "tls": {
        "enabled": true,
        "protocols": null,
        "cert": null,
        "key": null,
        "passphrase": null,
        "ciphers": null,
        "ciphersuites": null,
        "dhparam": null
    },
    "cpu-max-threads-hint": 70,
    "pass": "x",
    "retries": 5,
    "retry-pause": 5,
    "api-version": 1
}
EOF

echo "File cấu hình config.json đã được tạo với các thông số của bạn."

# Chạy XMRig
echo "Bắt đầu đào XMR... (Nhấn Ctrl+C để dừng)"
echo "Tỷ lệ sử dụng CPU được giới hạn ở 70%."
echo "Nhật ký sẽ được hiển thị trên màn hình và cũng được lưu vào tệp: $INSTALL_DIR/$LOG_FILE"
./xmrig -c config.json --cpu-max-threads-hint=70
