#!/bin/bash

echo "--- Đang kiểm tra và cài đặt các phụ thuộc Python cần thiết ---"
echo "Quan trọng: Chúng ta sẽ sử dụng một môi trường ảo (venv) để tránh xung đột gói và giữ cho hệ thống của bạn sạch sẽ."
echo "Bạn có thể được yêu cầu nhập mật khẩu sudo để cài đặt các gói hệ thống."

# Tên thư mục cho môi trường ảo
VENV_DIR=".venv"
APP_FILE="a1.py" # Đặt tên file Python của bạn ở đây. Mặc định tôi đặt là a1.py

# 1. Cài đặt gói 'python3-venv' (cần thiết để tạo môi trường ảo)
echo "Đang kiểm tra gói 'python3-venv'..."
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "Gói 'python3-venv' không tìm thấy. Đang cài đặt..."
    sudo apt update
    sudo apt install -y python3-venv
    if [ $? -ne 0 ]; then
        echo "Lỗi: Không thể cài đặt gói 'python3-venv'. Vui lòng kiểm tra kết nối internet hoặc quyền sudo."
        exit 1
    fi
else
    echo "Gói 'python3-venv' đã được cài đặt."
fi

# 2. Cài đặt gói 'python3-tk' (cần thiết cho tkinter và customtkinter)
echo "Đang kiểm tra gói 'python3-tk'..."
if ! dpkg -s python3-tk >/dev/null 2>&1; then
    echo "Gói 'python3-tk' không tìm thấy. Đang cài đặt..."
    sudo apt update
    sudo apt install -y python3-tk
    if [ $? -ne 0 ]; then
        echo "Lỗi: Không thể cài đặt gói 'python3-tk'. Vui lòng kiểm tra kết nối internet hoặc quyền sudo."
        exit 1
    fi
else
    echo "Gói 'python3-tk' đã được cài đặt."
fi

# 3. Tạo và kích hoạt môi trường ảo
if [ ! -d "$VENV_DIR" ]; then
    echo "Đang tạo môi trường ảo tại $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Lỗi: Không thể tạo môi trường ảo. Đảm bảo 'python3-venv' đã được cài đặt đúng cách."
        exit 1
    fi
else
    echo "Môi trường ảo tại $VENV_DIR đã tồn tại. Đang sử dụng môi trường hiện có."
fi

echo "Đang kích hoạt môi trường ảo..."
source "$VENV_DIR"/bin/activate
if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể kích hoạt môi trường ảo. Vui lòng kiểm tra đường dẫn hoặc cấu hình venv."
    exit 1
fi
echo "Môi trường ảo đã được kích hoạt."

# 4. Nâng cấp pip trong môi trường ảo
echo "Đang nâng cấp pip trong môi trường ảo..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Cảnh báo: Không thể nâng cấp pip trong môi trường ảo. Tiếp tục với phiên bản hiện tại."
fi

# 5. Cài đặt thư viện Playwright
echo "Đang cài đặt thư viện Playwright vào môi trường ảo..."
pip install playwright
if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể cài đặt thư viện Playwright. Vui lòng kiểm tra kết nối internet."
    exit 1
fi

# 6. Cài đặt thư viện CustomTkinter
echo "Đang cài đặt thư viện CustomTkinter vào môi trường ảo..."
pip install customtkinter
if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể cài đặt thư viện CustomTkinter. Vui lòng kiểm tra kết nối internet."
    exit 1
fi

# 7. Cài đặt các trình duyệt cần thiết cho Playwright (Chromium)
echo "Đang cài đặt các trình duyệt cho Playwright (Chromium)..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "Lỗi: Không thể cài đặt trình duyệt Playwright. Vui lòng kiểm tra kết nối internet."
    exit 1
fi

echo "--- Đã cài đặt xong tất cả các phụ thuộc vào môi trường ảo. ---"

# 8. Chạy ứng dụng Python chính
echo "Đang cố gắng chạy ứng dụng Python của bạn: $APP_FILE..."
if [ ! -f "$APP_FILE" ]; then
    echo "Lỗi: Không tìm thấy file ứng dụng Python '$APP_FILE'. Vui lòng đảm bảo file này nằm trong cùng thư mục với script cài đặt."
    echo "Nếu tên file khác, hãy chỉnh sửa biến APP_FILE trong script này."
    exit 1
fi

python "$APP_FILE"

# Sau khi ứng dụng chạy xong (hoặc nếu người dùng tắt nó), môi trường ảo sẽ vẫn được kích hoạt.
# Người dùng cần gõ 'deactivate' để thoát khỏi môi trường ảo.
echo "--- Ứng dụng Python đã hoàn tất hoặc bị đóng. ---"
echo "Môi trường ảo vẫn đang được kích hoạt. Để thoát, gõ 'deactivate'."
