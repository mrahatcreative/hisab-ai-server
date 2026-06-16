"""
Hisab Pata — Inference Server (FastAPI)
Integration layer between fine-tuned Qwen 1.5B and Flutter app.

Pipeline:
  User msg → [Rule Parser (skip for known patterns)] → Qwen 1.5B
    → Safety Validator → Response Formatter → Flutter

Flutter expects:
  POST /v1/chat/completions  {message, stream, context}
  → {choices: [{message: {content: text_with_data_blocks}}]}

  POST /v1/expense/confirm   → save to backend
  POST /v1/expense/cancel    → discard pending
"""

import json, os, re, sys, time, uuid
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ── Model loading ──────────────────────────────────────────────────────────
try:
    from unsloth import FastLanguageModel
    import torch
    _MODEL_AVAILABLE = True
except ImportError:
    _MODEL_AVAILABLE = False
    print("⚠ unsloth not available — running in mock mode for testing")

app = FastAPI(title="Hisab Pata SLM Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Server state ───────────────────────────────────────────────────────────
model = None
tokenizer = None
pending_expense = None   # last parsed expense awaiting confirm/cancel

# ── Category mapping ───────────────────────────────────────────────────────
BENGALI_CATEGORIES = {
    "Transport": "পরিবহন", "Mobile Recharge": "মোবাইল রিচার্জ", "Postage": "ডাক",
    "Publication": "প্রকাশনা", "Office Stationery": "অফিস স্টেশনারি",
    "Tips": "টিপস", "Donation": "দান", "Others": "অন্যান্য", "Salary": "বেতন",
}

# ── Pydantic models ────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    choices: list

# ── Pipeline components ────────────────────────────────────────────────────

def build_system_prompt(context: dict = None) -> str:
    ctx = context or {}
    cats = ctx.get("categories", [])
    balance = ctx.get("balance", 0)
    cat_str = ", ".join(cats) if cats else "Transport, Mobile Recharge, Postage, Publication, Office Stationery, Tips, Donation, Others, Salary"
    return f"book_type: personal\ncategories: {cat_str}\nbalance: {balance}"

def is_greeting_or_query(msg: str) -> bool:
    """Rule parser: skip model for simple intents."""
    msg_lower = msg.lower().strip()
    greetings = {"হাই", "হ্যালো", "হেলো", "hello", "hi", "hey", "আসসালামু আলাইকুম",
                 "সালাম", "শুভ সকাল", "good morning", "bye", "বাই", "ধন্যবাদ", "thanks",
                 "ওয়ালাইকুম আসসালাম", "নমস্কার"}
    if msg_lower in greetings:
        return True
    balance_kw = {"ব্যালেন্স", "balance", "কত টাকা আছে", "কত বাকি"}
    if any(kw in msg_lower for kw in balance_kw):
        return True
    return False

def parse_model_json(raw: str) -> dict:
    """Extract first valid JSON object from model output."""
    raw = raw.strip()
    # Find first { to last }
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        return {"intent": "unknown", "slots": {}, "action": "ask", "missing_fields": [], "question": raw[:200]}
    try:
        return json.loads(raw[start:end+1])
    except:
        return {"intent": "unknown", "slots": {}, "action": "ask", "missing_fields": [], "question": "দুঃখিত, বুঝতে পারিনি। আবার বলবেন?"}

def safety_validator(parsed: dict) -> dict:
    """Validate and fix common issues."""
    intent = parsed.get("intent", "unknown")
    slots = parsed.get("slots", {})
    action = parsed.get("action", "ask")
    confidence = parsed.get("confidence", 0.0)

    # Low confidence → ask for clarification
    if confidence < 0.3 and intent not in ("greeting", "help"):
        parsed["action"] = "ask"
        parsed["question"] = "আপনি কী বলতে চেয়েছেন? একটু পরিষ্কার করে বলুন।"

    # Note thickness check for expense/send
    if intent in ("expense", "send") and action == "confirm":
        note = slots.get("note", "")
        if not is_note_sufficient(note):
            parsed["action"] = "ask"
            parsed["missing_fields"] = parsed.get("missing_fields", []) + ["note_detail"]
            parsed["question"] = "কেন এবং কোথায় এই খরচ করছেন? বিস্তারিত জানান।"

    return parsed

def is_note_sufficient(note: str) -> bool:
    if not note or len(note) < 10:
        return False
    elements = 0
    if any(kw in note for kw in ["ভাড়া", "খরচ", "লাঞ্চ", "বাজার", "দান", "টিপস", "রিচার্জ", "কেনা"]):
        elements += 1
    if any(kw in note for kw in ["জন্য", "কারণ", "কাজে", "বাবদ", "হেতু", "পথে", "সময়", "লাগলো"]):
        elements += 1
    if any(kw in note for kw in ["থেকে", "যায়", "গিয়ে", "এসে", "হয়ে", "ফিরে"]):
        elements += 1
    if len(note) > 30:
        elements += 1
    return elements >= 3

def format_response_for_flutter(parsed: dict, context: dict = None) -> str:
    """Convert model JSON → human-readable Bengali text + [DATA] blocks."""
    ctx = context or {}
    intent = parsed.get("intent", "unknown")
    slots = parsed.get("slots", {})
    action = parsed.get("action", "ask")
    question = parsed.get("question", "")
    confidence = parsed.get("confidence", 0.0)
    response_text = parsed.get("response", "")
    balance = ctx.get("balance", 0)

    # ── Greeting/Help ──
    if intent in ("greeting", "help") and response_text:
        return response_text

    # ── Balance query ──
    if intent == "balance":
        return f"আপনার বর্তমান ব্যালেন্স: **{balance:,.0f} টাকা**।"

    # ── Summary ──
    if intent == "summary":
        return "গত মাসের সারসংক্ষেপ দেখাচ্ছি... [DATA type:summary]{\"period\":\"last_month\"}[/DATA]"

    # ── List ──
    if intent == "list":
        return "লেনদেনের তালিকা আনছি... [DATA type:list]{\"period\":\"recent\"}[/DATA]"

    # ── Ask for info ──
    if action == "ask":
        missing = parsed.get("missing_fields", [])
        if "amount" in missing:
            return f"আচ্ছা। **{question}**" if question else "কত টাকা? আমাকে পরিমাণটা জানান।"
        if "category" in missing:
            return f"কোন ক্যাটাগরিতে যোগ করব? **{question}**" if question else "কিসের জন্য খরচ? ক্যাটাগরি জানান।"
        if "note_detail" in missing:
            return f"**{question}**" if question else "কেন এবং কোথায় এই খরচ করছেন? বিস্তারিত জানান।"
        if "contact" in missing:
            return f"**{question}**" if question else "কার কাছে টাকা পাঠাব? নাম জানান।"
        return question or "বিস্তারিত জানান।"

    # ── Confirm expense ──
    if intent == "expense" and action == "confirm":
        amount = slots.get("amount", 0)
        cat = slots.get("category", "Others")
        cat_bn = BENGALI_CATEGORIES.get(cat, cat)
        note = slots.get("note", "")
        global pending_expense
        pending_expense = {"amount": amount, "category": cat, "note": note}
        return (
            f"✅ **খরচ যোগ করছি**\n\n"
            f"পরিমাণ: **{amount:,} টাকা**\n"
            f"ক্যাটাগরি: **{cat_bn}**\n"
            f"নোট: {note}\n\n"
            f"[DATA type:expense]{json.dumps(pending_expense, ensure_ascii=False)}[/DATA]"
        )

    # ── Confirm income ──
    if intent == "income" and action == "confirm":
        amount = slots.get("amount", 0)
        note = slots.get("note", "বেতন")
        return f"✅ **ইনকাম যোগ করছি**\n\nপরিমাণ: **{amount:,} টাকা**\nনোট: {note}"

    # ── Confirm send ──
    if intent == "send" and action == "confirm":
        amount = slots.get("amount", 0)
        contact = slots.get("contact", "")
        return f"✅ **সেন্ড করছি**\n\nপরিমাণ: **{amount:,} টাকা**\nপ্রাপক: **{contact}**"

    # ── Confirm edit/delete/approve/reject ──
    if action == "confirm":
        action_labels = {"edit": "এডিট", "delete": "ডিলিট", "approve": "অ্যাপ্রুভ", "reject": "রিজেক্ট"}
        label = action_labels.get(intent, intent)
        return f"✅ **{label}** করা হয়েছে।"

    return response_text or "বলুন, কী করতে চান?"

def inference(message: str, context: dict = None) -> str:
    """Run full pipeline: rule check → model → validate → format."""
    # 1. Rule check — skip model for simple intents
    if is_greeting_or_query(message):
        msg_lower = message.lower().strip()
        if any(kw in msg_lower for kw in ["ব্যালেন্স", "balance", "কত টাকা", "কত বাকি"]):
            parsed = {"intent": "balance", "slots": {}, "action": "confirm", "confidence": 0.95}
            return format_response_for_flutter(parsed, context)
        if msg_lower in ("bye", "বাই", "ধন্যবাদ", "thanks", "thank you"):
            return "ধন্যবাদ! Hisab AI ব্যবহার করার জন্য। আবার আসবেন।"
        return "হ্যালো! আমি Hisab AI — আপনার ব্যক্তিগত ফাইন্যান্স সহায়ক। M Rahat বানিয়েছেন। বলুন কী করতে চান?"

    # 2. Model inference
    system_msg = build_system_prompt(context)
    chatml = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": message},
    ]

    if model is not None:
        inputs = tokenizer.apply_chat_template(chatml, tokenize=True, add_generation_prompt=True, return_tensors="pt").to("cuda")
        outputs = model.generate(inputs, max_new_tokens=128, temperature=0.1, top_p=0.9, repetition_penalty=1.05)
        raw = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
    else:
        # Mock for testing without GPU
        raw = '{"intent":"expense","slots":{"amount":500,"category":"Transport","note":"অফিসের কাজে গুলশান যাওয়ার পথে রিক্সা ভাড়া বাবদ খরচ"},"action":"confirm","missing_fields":[],"confidence":0.88}'

    # 3. Parse model output
    parsed = parse_model_json(raw)

    # 4. Safety validate
    parsed = safety_validator(parsed)

    # 5. Format for Flutter
    return format_response_for_flutter(parsed, context)

# ── API endpoints ──────────────────────────────────────────────────────────

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    reply_text = inference(req.message, req.context)

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": reply_text},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

@app.post("/v1/expense/confirm")
async def confirm_expense():
    global pending_expense
    if not pending_expense:
        return {"status": "error", "message": "No pending expense"}
    # In production: save to backend API here
    result = {"status": "ok", "expense": pending_expense}
    pending_expense = None
    return result

@app.post("/v1/expense/cancel")
async def cancel_expense():
    global pending_expense
    pending_expense = None
    return {"status": "ok", "message": "Cancelled"}

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}

# ── Startup ────────────────────────────────────────────────────────────────

def load_model():
    global model, tokenizer
    if not _MODEL_AVAILABLE:
        print("⚠ Running in mock mode — no model loaded")
        return

    MODEL_PATH = "outputs/checkpoint-60"  # or your saved path
    if not os.path.exists(MODEL_PATH):
        print(f"⚠ Model not found at {MODEL_PATH} — loading base Qwen 1.5B instead")
        MODEL_PATH = "Qwen/Qwen2.5-1.5B-Instruct"

    print(f"Loading model from {MODEL_PATH}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        MODEL_PATH,
        max_seq_length=1024,
        dtype=None,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)
    print(f"✅ Model loaded. VRAM: {torch.cuda.max_memory_allocated()/1e9:.2f}GB")

if __name__ == "__main__":
    load_model()
    uvicorn.run(app, host="0.0.0.0", port=5328)
