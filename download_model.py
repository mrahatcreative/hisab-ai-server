#!/usr/bin/env python3
"""Download GGUF model from HuggingFace."""

from huggingface_hub import hf_hub_download
import os

repo = "unsloth/gemma-4-E4B-it-GGUF"
file = "gemma-4-E4B-it-Q4_K_M.gguf"

print(f"Downloading {file} (~4.98 GB) from {repo} ...")
path = hf_hub_download(repo_id=repo, filename=file, local_dir="/models")
print(f"Model cached at {path}")