#!/usr/bin/env python3
"""Download GGUF model from HuggingFace."""

from huggingface_hub import hf_hub_download
import os

repo = "unsloth/Qwen3.5-2B-GGUF"
file = "Qwen3.5-2B-Q4_K_M.gguf"

print(f"Downloading {file} (~1.27 GB) from {repo} ...")
path = hf_hub_download(repo_id=repo, filename=file, local_dir="/models")
print(f"Model cached at {path}")
