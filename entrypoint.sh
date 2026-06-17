#!/bin/bash
set -e

# মডেলের পাথ পরিবর্তন করে নতুন ৩বি মডেলের নাম দেওয়া হলো
MODEL_PATH="/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf"

echo "=== Hisab AI — Starting ==="

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Model should have been downloaded during build."
    exit 1
fi

echo "Model found at $MODEL_PATH"

# Start llama-server in background with optimized high-concurrency settings
echo "Starting llama-server..."
llama-server \
    -m "$MODEL_PATH" \
# Start llama-server with scalable context for 16 parallel slots (16 * 4096 = 65536)
llama-server \
    -m "$MODEL_PATH" \
    --port 8080 \
    --host 0.0.0.0 \
    --ctx-size 65536 \
    --parallel 16 \
    --threads 16 \
    --threads-batch 16 \
    --chat-template chatml \
    -ngl 0 &

LLAMA_PID=$!

# Wait for llama-server to be ready
echo "Waiting for llama-server..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
        echo "llama-server ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "llama-server failed to start"
        exit 1
    fi
    sleep 2
done

# Start router
echo "Starting router on port 5328..."
export LLAMA_URL=http://localhost:8080/v1/chat/completions
uvicorn router:app --host 0.0.0.0 --port 5328