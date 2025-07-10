#!/bin/bash
# curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/codecai.sh | bash



# === THÔNG SỐ CẦN ĐỔI (nếu cần) ===
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/test.py"
PYTHON_SCRIPT_NAME="autologin_idx.py"
INSTALL_DIR="$HOME/idx_auto_login"
VENV_DIR="$INSTALL_DIR/venv"

# === TẠO THƯ MỤC LƯU FILE ===
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || { echo "❌ Không thể vào thư mục $INSTALL_DIR"; exit 1; }

echo "📥 Đang tải file Python từ GitHub..."
curl -sL "$PYTHON_SCRIPT_URL" -o "$PYTHON_SCRIPT_NAME"
if [ $? -ne 0 ]; then
    echo "❌ Lỗi khi tải file Python"
    exit 1
fi
echo "✅ Tải thành công: $PYTHON_SCRIPT_NAME"

# === TẠO MÔI TRƯỜNG ẢO VÀ CÀI THƯ VIỆN ===
echo "🐍 Tạo môi trường ảo tại: $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "📦 Cài đặt thư viện cần thiết..."
pip install --upgrade pip
pip install playwright
playwright install

# === CHẠY FILE PYTHON ===
echo "🚀 Đang chạy script Python trong môi trường ảo..."
python "$PYTHON_SCRIPT_NAME"

# === THOÁT MÔI TRƯỜNG ẢO SAU KHI CHẠY ===
deactivate
echo "✅ Đã thoát môi trường ảo"

echo "🎉 Đã hoàn tất quá trình chạy tự động!"
