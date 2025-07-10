#!/bin/bash
# curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/codecai.sh | bash

# === CẤU HÌNH ===
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/test.py"
PYTHON_SCRIPT_NAME="test.py"
INSTALL_DIR="$HOME/idx_auto_login"
VENV_DIR="$INSTALL_DIR/venv"

echo "📁 Tạo thư mục cài đặt: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || { echo "❌ Không thể vào thư mục $INSTALL_DIR"; exit 1; }

# === TẠO MÔI TRƯỜNG ẢO ===
echo "🐍 Đang tạo môi trường ảo Python..."
python3 -m venv "$VENV_DIR"

# === KÍCH HOẠT VENV ===
echo "🔄 Kích hoạt môi trường ảo..."
source "$VENV_DIR/bin/activate"

# === CÀI PLAYWRIGHT VÀ PHỤ THUỘC ===
echo "📦 Cài đặt Playwright..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install playwright

# === CÀI TRÌNH DUYỆT CHO PLAYWRIGHT ===
"$VENV_DIR/bin/playwright" install

# === TẢI FILE PYTHON ===
echo "📥 Tải script Python từ GitHub..."
curl -sL "$PYTHON_SCRIPT_URL" -o "$PYTHON_SCRIPT_NAME"
if [ $? -ne 0 ]; then
    echo "❌ Lỗi khi tải script."
    [ -n "$VIRTUAL_ENV" ] && deactivate
    exit 1
fi

# === CHẠY FILE PYTHON ===
echo "🚀 Đang chạy script..."
"$VENV_DIR/bin/python" "$PYTHON_SCRIPT_NAME"

# === THOÁT MÔI TRƯỜNG ẢO ===
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

echo "✅ Hoàn tất quá trình."
