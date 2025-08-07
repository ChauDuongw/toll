#!/bin/bash
# curl -sL https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/codecai.sh | bash
# Chọn image Python 3.12 chính thức từ Docker Hub
FROM python:3.12-slim

# Cập nhật hệ thống và cài đặt curl để tải mã nguồn
RUN apt-get update && apt-get install -y curl

# Tải file vpn.py từ URL về container
RUN curl -o /vpn.py https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/vpn.py

# Thiết lập thư mục làm việc
WORKDIR /

# Cài đặt các yêu cầu (nếu có)
# Bạn có thể bổ sung dòng này nếu bạn có file requirements.txt hoặc cài đặt thư viện cần thiết
# RUN pip install -r requirements.txt

# Cài đặt ENTRYPOINT cho việc giữ container chạy
ENTRYPOINT ["python", "vpn.py"]

# Chạy shell sau khi hoàn tất vpn.py để giữ container sống và nhận lệnh
CMD ["sh"]
