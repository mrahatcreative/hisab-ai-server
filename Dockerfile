FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download llama-server binary from release tarball
RUN wget -qO /tmp/llama.tar.gz \
    https://github.com/ggml-org/llama.cpp/releases/download/b9567/llama-b9567-bin-ubuntu-x64.tar.gz && \
    tar xzf /tmp/llama.tar.gz -C /usr/local/bin/ --wildcards '*/llama-server' --strip-components=1 && \
    rm /tmp/llama.tar.gz && \
    chmod +x /usr/local/bin/llama-server

WORKDIR /app

COPY router.py .
COPY requirements-router.txt .
COPY entrypoint.sh /entrypoint.sh

RUN pip install -q --no-cache-dir -r requirements-router.txt && \
    chmod +x /entrypoint.sh

EXPOSE 5328 8080

ENTRYPOINT ["/entrypoint.sh"]
