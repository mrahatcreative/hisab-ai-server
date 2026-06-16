FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download llama-server binary
RUN wget -O /usr/local/bin/llama-server \
    https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-server-x86_64-linux && \
    chmod +x /usr/local/bin/llama-server

WORKDIR /app

COPY router.py .
COPY requirements-router.txt .
COPY entrypoint.sh /entrypoint.sh

RUN pip install -q --no-cache-dir -r requirements-router.txt && \
    chmod +x /entrypoint.sh

EXPOSE 5328 8080

ENTRYPOINT ["/entrypoint.sh"]
