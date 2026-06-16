#!/bin/bash
set -e

MODEL_CACHE="/models/gemma-3-1b-it-Q4_K_M.gguf"
HF_REPO="unsloth/gemma-3-1b-it-GGUF"
HF_FILE="gemma-3-1b-it-Q4_K_M.gguf"

echo "=== Hisab AI — Starting ==="

# Download model if not cached
if [ ! -f "$MODEL_CACHE" ]; then
    echo "Downloading model ($HF_FILE) from $HF_REPO ..."
    mkdir -p /models
    # Use HF transfer if available, else wget
    if command -v huggingface-cli &>/dev/null; then
        huggingface-cli download "$HF_REPO" "$HF_FILE" --local-dir /models
    else
        pip install -q huggingface-hub
        python3 -c "
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id='$HF_REPO', filename='$HF_FILE', local_dir='/models')
"
    fi
    echo "Download complete!"
else
    echo "Model cached at $MODEL_CACHE"
fi

# Start llama-server in background
echo "Starting llama-server..."
llama-server \
    -m "$MODEL_CACHE" \
    --port 8080 \
    --host 0.0.0.0 \
    --ctx-size 4096 \
    --parallel 3 \
    -ngl 0 &

LLAMA_PID=$!

# Wait for llama-server to be ready
echo "Waiting for llama-server..."
for i in $(seq 1 60); do
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        echo "llama-server ready!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "llama-server failed to start"
        exit 1
    fi
    sleep 2
done

# Start router
echo "Starting router on port 5328..."
export LLAMA_URL=http://localhost:8080/v1/chat/completions
uvicorn router:app --host 0.0.0.0 --port 5328
