#!/bin/bash
# Hisab AI — VPS Deploy Script
# VPS-এ SSH করে run করবেন

echo "=== Step 1: GGUF download ==="
mkdir -p /home/mrahat/models
wget -O /home/mrahat/models/hisab-ai.gguf \
  https://huggingface.co/unsloth/gemma-3-1b-it-GGUF/resolve/main/gemma-3-1b-it-Q4_K_M.gguf

echo "=== Step 2: Docker compose ==="
cd /home/mrahat/Documents/HisabPata/AI\ Server
docker compose up -d

echo "=== Step 3: Check ==="
sleep 5
curl -s http://localhost:5328/health | python3 -m json.tool

echo "=== Done! ==="
echo "Router: http://VPS_IP:5328"
echo "Test: curl http://VPS_IP:5328/v1/chat/completions -d '{\"message\":\"কে তুমি?\"}'"
