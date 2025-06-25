
#!/bin/bash
# curl -sL https://raw.githubusercontent.com/ChauDuongw/moungdungidx/refs/heads/main/0110/minhchau0110.sh | bash

# --- Cấu hình ---
# URL của file code Python cần "cài đặt" (tool.py)
PYTHON_CODE_URL="https://raw.githubusercontent.com/ChauDuongw/moungdungidx/refs/heads/main/tool2.py"
# Tên file code Python sau khi tải về (bạn muốn đặt là a1.py)
PYTHON_CODE_FILENAME="a1.py"

# URL của script cần chạy sau khi cài đặt (run_app.sh)
RUN_SCRIPT_URL="https://raw.githubusercontent.com/ChauDuongw/moungdungidx/refs/heads/main/run_app.sh"
# Tên file script sau khi tải về (run_app.sh)
RUN_SCRIPT_FILENAME="run_app.sh"

# Thư mục đích để lưu các file (ví dụ: thư mục hiện tại)
INSTALL_DIR="./" # Bạn có thể thay đổi thành "/opt/my_app/" hoặc "/usr/local/bin/" nếu muốn cài đặt hệ thống

echo "--- Bắt đầu quá trình cài đặt và chạy ---"

# --- 1. Tải và "cài đặt" (copy) file code Python ---
echo "Đang tải $PYTHON_CODE_URL và lưu thành $INSTALL_DIR$PYTHON_CODE_FILENAME..."
curl -sL "$PYTHON_CODE_URL" -o "$INSTALL_DIR$PYTHON_CODE_FILENAME"

# Kiểm tra xem việc tải và lưu file Python có thành công không
if [ $? -eq 0 ]; then
    echo "Tải và cài đặt $PYTHON_CODE_FILENAME thành công."
else
    echo "Lỗi: Không thể tải hoặc lưu $PYTHON_CODE_FILENAME. Vui lòng kiểm tra URL hoặc quyền ghi."
    exit 1 # Thoát với mã lỗi
fi

# --- 2. Tải script chạy (run_app.sh) ---
echo "Đang tải $RUN_SCRIPT_URL và lưu thành $INSTALL_DIR$RUN_SCRIPT_FILENAME..."
curl -sL "$RUN_SCRIPT_URL" -o "$INSTALL_DIR$RUN_SCRIPT_FILENAME"

# Kiểm tra xem việc tải script có thành công không
if [ $? -eq 0 ]; then
    echo "Tải $RUN_SCRIPT_FILENAME thành công."
else
    echo "Lỗi: Không thể tải hoặc lưu $RUN_SCRIPT_FILENAME. Vui lòng kiểm tra URL hoặc quyền ghi."
    exit 1 # Thoát với mã lỗi
fi

# Cấp quyền thực thi cho script run_app.sh
echo "Cấp quyền thực thi cho $RUN_SCRIPT_FILENAME..."
chmod +x "$INSTALL_DIR$RUN_SCRIPT_FILENAME"

# --- 3. Chạy script đã tải về (run_app.sh) ---
echo "Đang chạy $RUN_SCRIPT_FILENAME..."
# Điều hướng đến thư mục cài đặt trước khi chạy nếu cần
cd "$INSTALL_DIR" || { echo "Lỗi: Không thể vào thư mục cài đặt."; exit 1; }
./"$RUN_SCRIPT_FILENAME" # Chạy script đã cấp quyền thực thi

# Kiểm tra xem script run_app.sh có chạy thành công không
if [ $? -eq 0 ]; then
    echo "Chạy $RUN_SCRIPT_FILENAME thành công."
else
    echo "Lỗi: Chạy $RUN_SCRIPT_FILENAME thất bại."
fi

echo "--- Quá trình hoàn tất ---"
