import os, time
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Hisab AI Router")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LLAMA_URL = os.environ.get("LLAMA_URL", "http://localhost:8080/v1/chat/completions")

class ChatRequest(BaseModel):
    messages: list
    max_tokens: int = 256
    temperature: float = 0.3  # তাপমাত্রা কিছুটা বাড়িয়ে ০.৩ করা হলো যাতে ভাষা স্বাভাবিক হয়
    stream: bool = False

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    # Pass through backend's messages as-is — backend has the full system prompt
    processed_messages = req.messages.copy()

    payload = {
        "model": "hisab-ai",
        "messages": processed_messages,
        "max_tokens": req.max_tokens if req.max_tokens != 256 else 512,
        "temperature": req.temperature if req.temperature != 0.1 else 0.3,
        "stream": req.stream,
        "stop": ["<end_of_turn>"]
    }
    
    try:
        r = requests.post(LLAMA_URL, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Model unavailable: {str(e)}")

@app.get("/health")
async def health():
    try:
        r = requests.get(LLAMA_URL.replace("/v1/chat/completions", "/health"), timeout=5)
        model_ok = r.ok
    except:
        model_ok = False
    return {"status": "ok", "model_online": model_ok}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5328)