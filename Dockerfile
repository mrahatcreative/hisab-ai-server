FROM python:3.12-slim

ARG HF_TOKEN

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Download llama-server from release tarball
RUN wget -qO /tmp/llama.tar.gz \
    https://github.com/ggml-org/llama.cpp/releases/download/b9567/llama-b9567-bin-ubuntu-x64.tar.gz && \
    mkdir -p /opt/llama && \
    tar xzf /tmp/llama.tar.gz -C /opt/llama --strip-components=1 && \
    rm /tmp/llama.tar.gz && \
    chmod +x /opt/llama/llama-server && \
    ln -sf /opt/llama/llama-server /usr/local/bin/llama-server

ENV LD_LIBRARY_PATH=/opt/llama:$LD_LIBRARY_PATH

# Download GGUF model during build (separate script avoids Coolify ARG injection breaking multi-line strings)
COPY download_model.py /download_model.py
RUN pip install -q --no-cache-dir huggingface-hub && \
    python3 /download_model.py

WORKDIR /app

COPY router.py .
COPY requirements-router.txt .
COPY entrypoint.sh /entrypoint.sh

RUN pip install -q --no-cache-dir -r requirements-router.txt && \
    chmod +x /entrypoint.sh

EXPOSE 5328 8080

ENTRYPOINT ["/entrypoint.sh"]
