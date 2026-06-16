#!/usr/bin/env python3
"""Download GGUF model from HuggingFace."""

from huggingface_hub import hf_hub_download
import os

# Qwen2.5-3B-Instruct মডেলের জন্য রেপো এবং ফাইল পাথ আপডেট করা হলো
repo = "bartowski/Qwen2.5-3B-Instruct-GGUF"
file = "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

print(f"Downloading {file} (~2.02 GB) from {repo} ...")
path = hf_hub_download(repo_id=repo, filename=file, local_dir="/models")
print(f"Model cached at {path}")