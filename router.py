# Router — rule first, model second
# SOhoj query → rule diye reply, complex query → llama-server

import os, json, re, time, uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Hisab AI Router")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LLAMA_URL = os.environ.get("LLAMA_URL", "http://localhost:8080/v1/chat/completions")

class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    context: dict = None

# ─── Rule patterns ──────────────────────────────────────────────────────────

def get_balance_from_context(ctx: dict) -> str:
    b = ctx.get("balance", 0) if ctx else 0
    return f"আপনার বর্তমান ব্যালেন্স: {b:,.0f} টাকা।"

BALANCE_KW = {"ব্যালেন্স", "balance", "কত টাকা আছে", "কত টাকা", "বাকি কত", "টাকা আছে কত"}
GREETINGS = {"হাই", "হ্যালো", "hello", "hi", "hey", "আসসালামু আলাইকুম", "সালাম", "bye", "বাই", "ধন্যবাদ", "thanks"}
IDENTITY_KW = {"কে তুমি", "কে তোমাকে বানিয়েছে", "তোমার বানানো", "তোমার creator", "কে বানিয়েছে"}

SYSTEM_PROMPT = """তুমি Hisab AI — M Rahat বানিয়েছেন।
তোমার উত্তর সবসময় শুধুমাত্র JSON format-এ দাও।
কোনো natural text, greeting, বা comment থাকবে না।

Examples:

user: 500 টাকা খরচ করেছি পরিবহন বাবদ
assistant: {"intent":"add_expense","slots":{"amount":500,"category":"Transport","account_type":"personal"},"action":"ask_confirm","missing_fields":[],"confidence":0.95,"response":"পরিবহন বাবদ ৫০০ টাকা খরচ যোগ করছি?"}

user: কে তুমি?
assistant: {"intent":"identity","slots":{},"action":"respond","missing_fields":[],"confidence":1.0,"response":"আমি Hisab AI — M Rahat বানিয়েছেন।"}

user: ব্যালেন্স কত?
assistant: {"intent":"check_balance","slots":{"account_type":"personal"},"action":"respond","missing_fields":[],"confidence":1.0,"response":"আপনার ব্যালেন্স ১২৫০০ টাকা।"}

user: রহিম কে ২০০ টাকা সেন্ড করেছি
assistant: {"intent":"send_money","slots":{"amount":200,"recipient":"রহিম","account_type":"personal"},"action":"ask_confirm","missing_fields":[],"confidence":0.9,"response":"রহিম কে ২০০ টাকা পাঠানোর নিশ্চিত?"}"""

def rule_handle(msg: str, ctx: dict = None) -> dict:
    msg_lower = msg.lower().strip()

    # Greeting
    if msg_lower in GREETINGS:
        return {"intent":"greeting","slots":{},"action":"respond","missing_fields":[],"confidence":1.0,"response":"হ্যালো! আমি Hisab AI — M Rahat বানিয়েছেন। বলুন কী করতে চান?"}

    # Identity
    if any(kw in msg_lower for kw in IDENTITY_KW):
        return {"intent":"identity","slots":{},"action":"respond","missing_fields":[],"confidence":1.0,"response":"আমি Hisab AI — M Rahat বানিয়েছেন।"}

    # Balance
    if any(kw in msg_lower for kw in BALANCE_KW):
        return {"intent":"check_balance","slots":{"account_type":"personal"},"action":"respond","missing_fields":[],"confidence":1.0,"response":get_balance_from_context(ctx)}

    return None  # rule fail → model

def build_model_payload(msg: str, ctx: dict = None) -> dict:
    context_block = ""
    if ctx:
        cats = ctx.get("categories", [])
        bal = ctx.get("balance", 0)
        cat_str = ", ".join(cats) if cats else "Transport, Mobile Recharge, Postage, Publication, Office Stationery, Tips, Donation, Others, Salary"
        context_block = f"\nbook_type: personal\ncategories: {cat_str}\nbalance: {bal}"
    user_content = f"{SYSTEM_PROMPT}\n{context_block}\n\n{msg}"
    return {
        "model": "hisab-ai",
        "messages": [{"role": "user", "content": user_content}],
        "max_tokens": 256,
        "temperature": 0.1
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    # Step 1: Try rule
    ruled = rule_handle(req.message, req.context)
    if ruled is not None:
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "choices": [{"index": 0, "message": {"role": "assistant", "content": json.dumps(ruled, ensure_ascii=False)}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

    # Step 2: Call llama-server
    payload = build_model_payload(req.message, req.context)
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
