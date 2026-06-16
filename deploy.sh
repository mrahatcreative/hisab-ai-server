#!/bin/bash
# Hisab AI — VPS Deploy Script
# VPS-এ SSH করে run করবেন

echo "=== Step 1: Docker compose ==="
echo "GGUF auto-download hobe HuggingFace theke (unsloth/gemma-3-1b-it-GGUF)"
cd /home/mrahat/Documents/HisabPata/AI\ Server
HF_TOKEN="${HF_TOKEN:-}" docker compose up -d

echo "=== Step 3: Check ==="
sleep 5
curl -s http://localhost:5328/health | python3 -m json.tool

echo "=== Done! ==="
echo "Router: http://VPS_IP:5328"
echo "Test: curl http://VPS_IP:5328/v1/chat/completions -d '{\"message\":\"কে তুমি?\"}'"
