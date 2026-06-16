#!/usr/bin/env python3
"""Download GGUF model from HuggingFace."""

from huggingface_hub import hf_hub_download
import os

repo = "unsloth/gemma-3-1b-it-GGUF"
file = "gemma-3-1b-it-Q4_K_M.gguf"

print(f"Downloading {file} (806 MB) from {repo} ...")
path = hf_hub_download(repo_id=repo, filename=file, local_dir="/models")
print(f"Model cached at {path}")
