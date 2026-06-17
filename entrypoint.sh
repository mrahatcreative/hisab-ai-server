#!/bin/bash
set -e

MODEL_PATH="/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf"

echo "=== Hisab AI — Starting ==="

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Model should have been downloaded during build."
    exit 1
fi

echo "Model found at $MODEL_PATH"

# Cleanup function on container exit
cleanup() {
    echo "Shutting down processes..."
    if [ -n "$LLAMA_PID" ]; then kill $LLAMA_PID 2>/dev/null || true; fi
    if [ -n "$ROUTER_PID" ]; then kill $ROUTER_PID 2>/dev/null || true; fi
}
trap cleanup EXIT SIGTERM SIGINT

# Start llama-server with exact parameters
echo "Starting llama-server with exact parameters..."
llama-server -m "$MODEL_PATH" --port 8080 --host 0.0.0.0 --ctx-size 65536 --parallel 16 --threads 16 --threads-batch 16 --chat-template chatml -ngl 0 &
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

# Start router in background to monitor both processes
echo "Starting router on port 5328..."
export LLAMA_URL=http://localhost:8080/v1/chat/completions
uvicorn router:app --host 0.0.0.0 --port 5328 &
ROUTER_PID=$!

# Monitor both background processes. If any fails, exit container.
while true; do
    if ! kill -0 $LLAMA_PID 2>/dev/null; then
        echo "CRITICAL: llama-server died!"
        exit 1
    fi
    if ! kill -0 $ROUTER_PID 2>/dev/null; then
        echo "CRITICAL: router died!"
        exit 1
    fi
    sleep 5
done