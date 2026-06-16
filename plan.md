# Hisab Pata — AI Dataset Plan (Qwen 1.5B Optimized)

> Small model = pattern learner, not reasoning engine. এই design সেই reality মাথায় রেখে বানানো।

---

## Core Architecture Principle

```
                     ┌──────────────────────────────────────────────┐
                     │           BACKEND PIPELINE                  │
                     │                                              │
User Input ──────►   │  ┌──────────┐   ┌──────────┐   ┌─────────┐  │
                     │  │  RULE    │──►│  QWEN    │──►│ VALIDATOR│──► API
                     │  │  PARSER  │   │  1.5B    │   │         │  │
                     │  │ (regex + │   │ (extract)│   │ (safety │  │
                     │  │ keywords)│   │          │   │  check) │  │
                     │  └──────────┘   └──────────┘   └─────────┘  │
                     │                                              │
                     │  If rule matches → skip LLM (fast path)     │
                     │  If unclear → LLM extracts                   │
                     └──────────────────────────────────────────────┘
```

**Rule parser (regex + keywords)**: handles patterns like "ব্যালেন্স কত?", "বেতন এসেছে ৫০০০০" — no LLM needed. Saves latency + cost.

> ⚠️ **Rule parser is a speed optimization, NOT intelligence replacement.** Complex inputs ("আজ ৫০০ lunch আর বাস আর dinner") will never be fully covered by regex. Don't let it grow into a monster rule engine. Keep it minimal — only exact/fixed patterns.

**Qwen 1.5B**: only invoked for complex/fuzzy inputs.

**Validator**: re-checks model output before any action. Never trusts the model blindly.

---

## 1. Model Output Format (Simplified — Flat, Shallow)

এটাই model-এর শুধু output। বাকি সব backend handle করবে।

### Financial Transaction Output
```json
{
  "intent": "expense",
  "slots": {
    "amount": 500,
    "category": "Transport",
    "note": "বাস ভাড়া"
  },
  "action": "confirm",
  "missing_fields": [],
  "question": null
}
```

### Greeting / Introduction Output
```json
{
  "intent": "greeting",
  "slots": {},
  "action": "greeting",
  "response": "হ্যালো! আমি Hisab AI। M Rahat আমাকে বানিয়েছেন। কী সাহায্য দরকার?",
  "confidence": 1.0
}
```

### Rules:
- `intent`: 1 string (12 possible values)
- `slots`: flat key-value. NO nested objects, NO status field
- `action`: `"confirm" | "ask" | "greeting"`
- `missing_fields`: string array
- `question`: string (only when action = "ask")
- `response`: string (only when action = "greeting" — natural language reply)
- `confidence`: float 0.0–1.0 (lightweight — how sure the model is)

### ⚠️ Critical: `note` Field Is NOT Optional

`note` is not a casual description. It's the **audit trail** of the transaction.

```
THIN note (REJECT):    "রিক্সা ভাড়া"
THICK note (ACCEPT):   "জরুরী কাজে পল্টন থেকে মগবাজারে অফিসে যাতায়াত এর জন্য রিক্সা ভাড়া বাবদ খরচ"
```

A note must contain **3+ context elements** from this list:
| Element | Question | Example |
|---------|----------|---------|
| WHAT | কি করছেন? | রিক্সা ভাড়া, lunch, বাজার |
| WHY | কেন? | জরুরী কাজে, অফিসের জন্য, অসুস্থ বলে |
| WHERE | কোথায়? | পল্টন থেকে মগবাজারে, বাড্ডা থেকে গুলশান |
| WHEN (if not in date field) | কখন? | সকালে, রাত ৯টায় |
| WHO (if relevant) | কার সাথে? | রহিমের সাথে, পরিবার নিয়ে |
| DETAIL | বিস্তারিত | অফিসে যাতায়াত, ডাক্তার দেখাতে |

**Training data MUST teach this pattern:**
- Input with thin note → AI asks for more detail
- Input with thick note → AI proceeds to confirm
- Multi-turn conversation where AI extracts elements one by one

### Confidence Score Logic
```
confidence ≥ 0.7  → backend proceeds (but validator still checks)
confidence 0.4–0.7 → backend re-asks for unclear fields
confidence < 0.4  → backend falls back to rule parser or "বুঝতে পারিনি"
```

⚠️ **WARNING: Confidence calibration is NOT reliable on Qwen 1.5B.**  
→ **Confidence is a SOFT HINT, not a decision gate.**  
The real decision gate = validator rules + missing field check + business logic + note completeness check.

Training data: include confidence in examples. Low-confidence examples teach the model when to be unsure.

### 12 Intents (Only, Not 20)

| Intent | Trigger |
|--------|---------|
| `expense` | খরচ/দিয়েছি/লাগবে + amount |
| `income` | ইনকাম/পেয়েছি/এসেছে + amount |
| `send` | সেন্ড/পাঠাই + contact + amount |
| `balance` | ব্যালেন্স/কত বাকি |
| `summary` | summary/কত খরচ/রিপোর্ট |
| `list` | দেখাও/লিস্ট/লেনদেন |
| `greeting` | হাই/হ্যালো/কেমন আছো |
| `help` | কি করতে পারো/কিভাবে |
| `edit` | পরিবর্তন/বদলাও/এডিট |
| `delete` | ডিলিট/মুছে ফেল/বাদ দাও |
| `approve` | হ্যাঁ/ঠিক আছে/approve |
| `reject` | না/বাতিল/reject |

> `add_expense` → `expense` (shorter = easier for small model)  
> `add_income` → `income`  
> merged `query_*` into 3: `balance`, `summary`, `list`

---

## 2. Training Example Format

### Full Example (Single Turn — Thick Note)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "book_type: personal\ncategories: Transport, Mobile Recharge, Others, Salary\nbalance: 12500"
    },
    {
      "role": "user",
      "content": "আজ জরুরী কাজে পল্টন থেকে মগবাজারে অফিসে যাতায়াত এর জন্য ৫০০ টাকা রিক্সা ভাড়া খরচ করেছি"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{\"amount\":500,\"category\":\"Transport\",\"note\":\"জরুরী কাজে পল্টন থেকে মগবাজারে অফিসে যাতায়াত এর জন্য রিক্সা ভাড়া বাবদ খরচ\",\"date\":\"2026-06-15\"},\"action\":\"confirm\",\"missing_fields\":[],\"confidence\":0.95}"
    }
  ]
}
```

### Thin Note → AI Asks for Details (Multi-Turn)

```json
{
  "messages": [
    {
      "role": "system",
      "content": "categories: Transport, Mobile Recharge, Others, Salary"
    },
    {
      "role": "user",
      "content": "আজ ৫০০ টাকা রিক্সা ভাড়া খরচ করেছি"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{\"amount\":500,\"category\":\"Transport\",\"note\":\"রিক্সা ভাড়া\",\"date\":\"2026-06-15\"},\"action\":\"ask\",\"missing_fields\":[\"note_detail\"],\"question\":\"কোন কাজে রিক্সা ভাড়া করছিলেন? কোথায় যাচ্ছিলেন? বিস্তারিত জানান।\",\"confidence\":0.88}"
    },
    {
      "role": "user",
      "content": "পল্টন থেকে মগবাজারে অফিসের কাজে গিয়েছিলাম"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{\"amount\":500,\"category\":\"Transport\",\"note\":\"অফিসের কাজে পল্টন থেকে মগবাজারে যাতায়াত এর জন্য রিক্সা ভাড়া বাবদ খরচ\",\"date\":\"2026-06-15\"},\"action\":\"confirm\",\"missing_fields\":[],\"confidence\":0.93}"
    }
  ]
}
```

### Note Detail Gathering — Progressive Elements

```
Turn 1:
  User: "আজ ৫০০ টাকা খরচ করেছি"
  AI: "কিসের জন্য খরচ করছেন?"

Turn 2:
  User: "রিক্সা ভাড়া"
  AI (note="রিক্সা ভাড়া" — only 1 element, THIN):
    "কোথায় গিয়েছিলেন? কোন কাজে?"

Turn 3:
  User: "পল্টন থেকে মগবাজারে অফিস কাজে"
  AI (note="অফিস কাজে পল্টন থেকে মগবাজারে রিক্সা ভাড়া" — 3 elements, THICK now):
    → confirm
```

### Low Confidence Example
```json
{
  "messages": [
    {
      "role": "system",
      "content": "categories: Transport, Mobile Recharge, Others, Salary"
    },
    {
      "role": "user",
      "content": "আজ কিছু টাকা খরচ করেছি"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{},\"action\":\"ask\",\"missing_fields\":[\"amount\"],\"question\":\"কত টাকা খরচ করছেন?\",\"confidence\":0.35}"
    }
  ]
}
```

### Missing Info Example

```json
{
  "messages": [
    {
      "role": "system",
      "content": "book_type: personal\ncategories: Transport, Mobile Recharge, Others, Salary"
    },
    {
      "role": "user",
      "content": "৫০০ টাকা খরচ করেছি"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{\"amount\":500},\"action\":\"ask\",\"missing_fields\":[\"category\"],\"question\":\"কিসের জন্য খরচ করছেন?\"}"
    }
  ]
}
```

### Multi-Turn Example

```json
{
  "messages": [
    {
      "role": "system",
      "content": "categories: Transport, Mobile Recharge, Others, Salary"
    },
    {
      "role": "user",
      "content": "৫০০ টাকা খরচ করেছি"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{\"amount\":500},\"action\":\"ask\",\"missing_fields\":[\"category\"],\"question\":\"কিসের জন্য?\"}"
    },
    {
      "role": "user",
      "content": "অফিসের কাজে বাসে গিয়েছিলাম"
    },
    {
      "role": "assistant",
      "content": "{\"intent\":\"expense\",\"slots\":{\"amount\":500,\"category\":\"Transport\",\"note\":\"অফিসের কাজে বাস\"},\"action\":\"confirm\",\"missing_fields\":[]}"
    }
  ]
}
```

> **Key**: multi-turn = just more messages in the array. No separate `conversation_state` object.  
> Model learns from message history naturally. Backend stores the history.

### ⚠️ But: Context Window Limits

তুমি pure message history-র উপর ভরসা করলে production edge cases এ break করবে। কারণ:
1. 1.5B model attention limited
2. Long context → earlier slot retention unreliable
3. Mid-conversation corrections miss হতে পারে

**Fix: Backend maintains a lightweight session_state and injects into system prompt**

```python
session_state = {
    "amount": 500,       # from turn 1
    "category": None,    # still missing
    "intent": "expense",
    "last_action": "ask"  # what AI did last
}

system_prompt = f"""
categories: Transport, Mobile Recharge, Others, Salary
current_session: amount=500, intent=expense, missing=category
"""
```

This gives the model a direct hint without relying on attention span.

---

## 3. Category Handling (Soft, Not Hard)

### Problem with old approach
"Never invent categories" → Qwen 1.5B তে enforce করা impossible। Model hallucinate করবেই কখনো কখনো।

### Solution: Soft Classification + Backend Validation Layer

```
Model tries its best → outputs category string
                          │
                          ▼
Backend checks: is it in available_categories?
    YES → use it
    NO  → fuzzy match against available list
           if still no match → use "Others" + log
```

### Training Approach
Training data তে `category` field সবসময় available list থেকে দাও। কিন্তু inference এ model miss করলে, backend fixed করবে।

```
Train:  category → always correct (from available list)
Infer:  category → model's best guess → backend validates/fixes
```

---

## 4. Date & Amount Normalization

### What Model Does
Model শুধু raw text extract করে। Normalization backend করে।

```
Model output → "slots": { "date": "আজ", "amount": 500 }
Backend      → "আজ" → 2026-06-15, 500 → 500.0
```

### Exception: Numeric Amounts
Model সবসময় numeric এ output করে (easy pattern):
- "পাঁচশ টাকা" → 500 (model learns this mapping)
- "৫০০" → 500
- "500" → 500

Textual Bengali numbers (পাঁচশ, দুই হাজার) → training data তে রাখো, model শিখবে। কিন্তু miss করলে backend fallback থাকবে।

---

## 5. Multi-Turn (No State Machine)

### Old (over-engineered)
```json
{
  "conversation_state": {
    "turn_number": 2,
    "previous_messages": [...],
    "known_fields": { "amount": 500 },
    "active_intent": "add_expense"
  }
}
```

### New (just messages array)
```
Turn 1:
  user: "৫০০ টাকা খরচ করেছি"
  assistant: {"intent":"expense","slots":{"amount":500},"action":"ask","missing_fields":["category"]}

Turn 2:
  user: "লাঞ্চ"
  assistant: {"intent":"expense","slots":{"amount":500,"category":"Others","note":"লাঞ্চ"},"action":"confirm"}
```

**Why this works**: Qwen 1.5B sees the full message history in context. Pattern: "user said amount → assistant asked for category → user said lunch → assistant fills category from context." No explicit state needed.

### Correction Handling (Critical Pattern)

```
Turn 1:
  user: "গতকাল ৩০০ খরচ করেছি"
  assistant: {"intent":"expense","slots":{"amount":300,"date":"2026-06-14"},"action":"ask","missing_fields":["category"]}
  user: "lunch"
  assistant: {"intent":"expense","slots":{"amount":300,"date":"2026-06-14","category":"Others","note":"lunch"},"action":"confirm"}

Turn 2:
  user: "ওইটা না, ২০০ ছিল"
  assistant: {"intent":"edit","slots":{"amount":200},"action":"confirm"}
```

Model learns: when user says "না" + correction → change the slot.

---

## 6. Category Mapping (For Training Data)

### Bengali → English Mapping

| User Says | Category Output |
|-----------|----------------|
| বাস, ট্রেন, ভাড়া, রিকশা, সিএনজি | Transport |
| রিচার্জ, মোবাইল, ফোন | Mobile Recharge |
| ডাক, পোস্ট, পোস্টেজ | Postage |
| বই, প্রকাশনা, পত্রিকা | Publication |
| স্টেশনারি, কলম, খাতা | Office Stationery |
| টিপস, বখশিশ | Tips |
| দান, সদকা, জাকাত | Donation |
| বেতন, সেলারি | Salary |
| lunch, লাঞ্চ, খাওয়া, ডিনার, breakfast | Others |
| বাজার, কাপড়, চিকিৎসা, ওষুধ | Others |
| সেন্ড, পাঠানো | Send |

**Training data এ ১০০% বাংলা → English mapping রেখো।** Model শিখবে "বাস" → "Transport" pattern.

---

## 7. Edge Cases (Training Data)

### Type 1: Spelling Mistakes
```
"আজ ৫০০ টকা খচর করেছি"
→ {"intent":"expense","slots":{"amount":500,"note":"খচর"}}
```

### Type 2: Banglish
```
"ajke 500 taka lunch khorch"
→ {"intent":"expense","slots":{"amount":500,"note":"lunch"}}
```

### Type 3: Mixed
```
"আজ 500 taka lunch খরচ"
→ {"intent":"expense","slots":{"amount":500,"note":"lunch"}}
```

### Type 4: Bengali Numbers
```
"পাঁচশ টাকা খরচ করেছি lunch এ"
→ {"intent":"expense","slots":{"amount":500,"note":"lunch"}}
```

### Type 5: No Amount
```
"আজ খরচ করেছি lunch এ"
→ {"intent":"expense","slots":{},"action":"ask","missing_fields":["amount"],"question":"কত টাকা?"}
```

### Type 6: Unknown Category
```
"আজ ৩০০ টাকা নেটফ্লিক্স দিয়েছি"
→ {"intent":"expense","slots":{"amount":300,"category":"Others","note":"নেটফ্লিক্স"},"action":"confirm"}
```
(Backend fuzzy-match করবে বা Others রাখবে)

### Type 7: Multiple Transactions (One Slot)
Model only handles ONE transaction per turn. Multiple transactions = split into separate turns by backend.

### Type 8: Thin Note → AI Pushes for Detail

```
User: "আজ ৫০০ টাকা খরচ করেছি lunch এ"
AI (note="lunch" — THIN, only 1 element):
  → {"action":"ask","missing_fields":["note_detail"],"question":"কোথায় lunch করছিলেন? কার সাথে?"}

User: "অফিসের ক্যান্টিনে রহিমের সাথে"
AI (note="অফিসের ক্যান্টিনে রহিমের সাথে lunch" — 3 elements: WHAT+lunch, WHERE+ক্যান্টিন, WHO+রহিম):
  → confirm
```

### Type 9: User Resists Detail

```
User: "খরচ করেছি ২০০, lunch"
AI: "বিস্তারিত জানান"
User: "শুধু lunch, বেশি কিছু না"
AI (must decide): if user clearly resists → accept thin note with low confidence flag.
  Backend logs: "note_resisted" for later review.
```

Training data MUST include examples where user gives:
- Thin note → AI asks (200+ examples)
- Medium note → AI asks for one more element (100+ examples)
- Thick note → AI proceeds (300+ examples)
- User resists → AI logs and proceeds (30+ examples)

---

## 8. Synthetic Data Generation (Simplified)

### Phase 1: Template-Based (1,500 examples)

```python
templates = {
    "expense": [
        "আজ {amount} টাকা {category_bn} খরচ",
        "{amount} টাকা {note}",
        "গতকাল {amount} {category_bn} দিয়েছি",
        "ajke {amount} taka {category_bl} khorch",
        "{amount}/- {note_bn} খরচ",
    ],
    "income": [
        "{amount} টাকা ইনকাম",
        "বেতন এসেছে {amount}",
        "{amount} taka paichi",
    ],
    "send": [
        "{contact} কে {amount} সেন্ড",
        "{contact} ke {amount} pathaisi",
    ]
}
```

### Phase 2: LLM-Based (3,500 examples)
Teacher LLM দিয়ে generate করাও। কিন্তু **Qwen 1.5B-format output** এ — not the complex schema.

### Phase 3: Multi-Turn (1,000 threads)
Each thread = 2-4 messages. Corrections included.

### Phase 4: Edge Cases (2,000 examples)
Spelling mistakes, Banglish (30-40% of total data), missing fields, Bengali numbers, vague inputs.

---

## 9. Dataset Distribution

### MVP (1,000 examples)

| Type | Count |
|------|-------|
| expense (full info) | 250 |
| expense (partial → ask) | 100 |
| income (full) | 100 |
| income (partial → ask) | 50 |
| send (full) | 50 |
| send (partial) | 30 |
| balance query | 50 |
| summary query | 50 |
| list query | 50 |
| greeting/help | 100 |
| edit/delete | 50 |
| approve/reject | 20 |
| Banglish inputs (30%) | 150 |
| Spelling mistakes | 100 |
| Thin note → push for detail | 150 |
| Thick note → direct confirm | 50 |

### Good Model (8,000 examples)

| Type | Count |
|------|-------|
| expense | 2,500 |
| income | 1,000 |
| send | 500 |
| queries (balance/summary/list) | 800 |
| greeting/help | 300 |
| edit/delete | 200 |
| approve/reject | 200 |
| Multi-turn threads | 1,000 |
| Note detail gathering (multi-turn) | 500 |
| Edge cases | 1,500 |

---

## 10. Production Pipeline (Full Flow)

```
                         USER INPUT
                             │
                             ▼
                  ┌─────────────────────┐
                  │  1. RULE PARSER     │
                  │  (regex + keywords) │
                  └──────────┬──────────┘
                             │
                    ┌────────┴────────┐
                    │ MATCH?          │
                    └────────┬────────┘
                    YES      │      NO
                    ┌────────┘      ┌────────┐
                    ▼               ▼        │
             ┌────────────┐  ┌────────────┐  │
             │ FAST PATH  │  │ 2. QWEN   │  │
             │ (no LLM)   │  │  1.5B     │  │
             │ direct API │  │ (extract) │  │
             └────────────┘  └─────┬──────┘  │
                                   │         │
                                   ▼         │
                          ┌──────────────┐   │
                          │ 3. SAFETY    │   │
                          │   VALIDATOR  │   │
                          └──────┬───────┘   │
                                 │           │
                          ┌──────┴──────┐    │
                          │ PASS?       │    │
                          └──────┬──────┘    │
                          YES    │    NO     │
                          ┌──────┘    ┌──────┘
                          ▼           ▼
                   ┌──────────┐ ┌──────────┐
                   │ 4. API   │ │ FALLBACK │
                   │  CALL    │ │ re-ask   │
                   └──────────┘ └──────────┘
```

### Step 1: Rule Parser (Before LLM)

```python
def rule_parse(user_input: str) -> dict | None:
    """If pattern matches, return structured output directly. NO LLM needed."""

    # Exact match: balance query
    if user_input.strip() in ["ব্যালেন্স কত?", "balance", "কত টাকা আছে?", "আমার ব্যালেন্স"]:
        return {"intent": "balance", "slots": {}, "action": "confirm", "confidence": 1.0}

    # Regex match: বেতন এসেছে {amount}
    m = re.search(r"(বেতন|সেলারি|salary)\s*(এসেছে|পেয়েছি|পাইছি|আসছে)?\s*(\d+)", user_input)
    if m:
        return {"intent": "income", "slots": {"amount": int(m.group(3)), "category": "Salary",
                "note": f"{m.group(1)} {m.group(2) or ''}".strip()}, "action": "confirm", "confidence": 0.95}

    # Regex match: {amount} + {known pattern}
    # ... more patterns

    return None  # No rule matched → pass to LLM
```

### Step 2: Safety Validator (After LLM)

```python
def safety_validator(model_output: dict) -> dict:
    """NEVER trust the model. Re-check everything."""

    intent = model_output.get("intent")
    slots = model_output.get("slots", {})
    action = model_output.get("action")
    confidence = model_output.get("confidence", 0.5)

    # SAFETY RULE 1: Low confidence → always ask
    if confidence < 0.4:
        return {"action": "ask", "question": "বুঝতে পারিনি। আবার বলবেন?", "original": model_output}

    # SAFETY RULE 2: Missing critical fields → force ask
    if intent in ("expense", "income", "send") and "amount" not in slots:
        return {"action": "ask", "question": "কত টাকা?", "missing_fields": ["amount"]}

    # SAFETY RULE 3: amount present but <= 0
    if "amount" in slots and slots["amount"] <= 0:
        return {"action": "ask", "question": "পরিমাণ কি ঠিক আছে? ০ বা ঋণাত্মক টাকা লাগতে পারে না।"}

    # SAFETY RULE 4: Action override — model says confirm but we re-check
    if action == "confirm" and intent in ("expense", "income", "send"):
        missing = [f for f in ("amount", "category") if f not in slots]
        if missing:
            return {"action": "ask", "question": f"নিচের তথ্য দিন: {', '.join(missing)}", "missing_fields": missing}

    # SAFETY RULE 5: Category fix + log
    if "category" in slots:
        available = user_context.get("available_categories", [])
        if slots["category"] not in available:
            matched = fuzzy_match(slots["category"], available)
            if matched:
                slots["category"] = matched
            else:
                slots["category"] = "Others"
                log_unknown_category(slots["category"], model_output)  # ← LOG FOR RETRAINING

    # SAFETY RULE 6: Note completeness check (CRITICAL)
    if intent in ("expense", "income", "send") and "note" in slots:
        if not is_note_sufficient(slots["note"]):
            return {
                "action": "ask",
                "question": "বিস্তারিত জানান। কীভাবে, কেন, কোথায় এই খরচ করছেন?",
                "missing_fields": ["note_detail"],
                "current_note": slots["note"]
            }

    return {"action": action, "slots": slots, "intent": intent}

def is_note_sufficient(note: str) -> bool:
    """A note must contain 3+ context elements to be sufficient."""
    elements = 0
    # Check for WHAT (expense type)
    if any(kw in note for kw in ["ভাড়া", "খরচ", "লাঞ্চ", "বাজার", "দান", "টিপস"]):
        elements += 1
    # Check for WHY (reason)
    if any(kw in note for kw in ["জন্য", "কারণ", "কাজে", "বাবদ", "হেতু"]):
        elements += 1
    # Check for WHERE (location)
    if any(kw in note for kw in ["থেকে", "যায়", "গিয়ে", "এ", "তে"]):
        elements += 1
    # Check for DETAIL (specific context)
    if len(note) > 30:  # Longer notes likely have more detail
        elements += 1
    # Check for WHO (person reference)
    if any(kw in note for kw in ["সাথে", "জন্য", "দিয়ে"]):
        if len(note) > 20:
            elements += 1

    return elements >= 3
```

### Step 3: Multi-Transaction Pre-Split

```python
def pre_split_input(user_input: str) -> list[str]:
    """Split "lunch ২০০, bus ১০০" → ["lunch ২০০", "bus ১০০"]"""
    separators = [", ", "। ", " আর ", " and ", " + ", " , "]
    for sep in separators:
        if sep in user_input:
            parts = user_input.split(sep)
            if len(parts) > 1 and all(has_amount(p) for p in parts):
                return parts
    return [user_input]  # Single transaction
```

### Step 4: Debug Field (Internal, Not Sent to User)

```python
def build_debug(model_output, safe_output, rule_triggered=None):
    return {
        "model_raw": model_output,
        "validator_override": model_output != safe_output,
        "why_ask": safe_output.get("missing_fields", []),
        "why_override": "low confidence" if model_output.get("confidence", 1.0) < 0.4 else None,
        "rule_triggered": rule_triggered,
        "category_fallback": safe_output.get("category_fallback"),
    }
```

### Step 5: Dynamic Subcategory Log (Prevent "Others" Explosion)

```python
def log_subcategory(user_input: str, model_output: dict, final_category: str):
    """Every time user says something specific → log the raw term."""
    if final_category == "Others":
        raw_term = extract_raw_category_term(user_input)
        if raw_term:
            db.log_event("subcategory_others", {
                "raw_term": raw_term,
                "user_id": user_context.user_id,
                "timestamp": now()
            })
            # After 10+ occurrences of same term → flag for new category
```

⚠️ **Without this, "Others" will silently consume all unique spend patterns** → analytics useless.

### Step 6: Full Handler

```python
def handle_user_input(user_input: str, user_context: dict, session_state: dict) -> dict:
    # Phase A: Inject session state into system prompt
    system_prompt = build_prompt(user_context, session_state)

    # Phase B: Pre-split multi-transactions
    inputs = pre_split_input(user_input)

    responses = []
    for single_input in inputs:
        # Phase C: Try rule parser first (speed optimization only)
        rule_result = rule_parse(single_input)
        if rule_result:
            rule_triggered = rule_result.get("rule_name")
            responses.append(execute_action(rule_result, user_context))
            # Log rule match for coverage tracking
            log_event("rule_parser_match", {"rule": rule_triggered, "input": single_input})
            continue

        # Phase D: LLM extraction
        model_output = qwen_extract(single_input, system_prompt)

        # Phase E: Safety check (NEVER trust the model)
        safe_output = safety_validator(model_output, user_context)

        # Phase F: Build debug trail
        debug = build_debug(model_output, safe_output)
        log_event("model_output", debug)

        # Phase G: Log subcategories for Others
        log_subcategory(single_input, model_output, safe_output.get("category"))

        # Phase H: Execute or ask
        responses.append(execute_action(safe_output, user_context, debug))

    # Phase I: Update session_state for next turn
    update_session_state(session_state, responses)

    return responses
```

---

## 11. Evaluation Metrics (Realistic)

| Metric | Realistic Target | Why |
|--------|-----------------|-----|
| Intent accuracy | >85% | 1.5B model, 12 classes |
| Slot presence | >80% | Did it extract the main fields? |
| Category hallucination | <15% | Will happen, backend fixes |
| JSON parse rate | >95% | Simple flat JSON, easy |
| Multi-turn slot fill | >70% | Model uses context |
| Bengali understanding | >85% | Main language |
| Banglish understanding | >70% | Harder for small model |

---

## 11. Logging & Retraining Loop

### Why This Matters (Critical)
Three silent killers in this architecture:
1. **"Others" category explosion** — user says Netflix/Uber/Spotify → all go to Others → analytics useless
2. **Rule parser false confidence** — regex matches but wrong intent → silent failure
3. **Validator overrides** — model says X, validator says Y → need to track why

### Log Schema
```json
{
  "event": "category_fallback",
  "user_input": "আজ ৩০০ টাকা নেটফ্লিক্স দিয়েছি",
  "model_raw": "Netflix",
  "final_category": "Others",
  "confidence": 0.85,
  "timestamp": "2026-06-15T10:30:00Z",
  "user_id": 123
}
```

### All Events to Log

| Event | Why | Action |
|-------|-----|--------|
| `category_fallback` | Model said X → ended in Others | Cluster terms → suggest new categories |
| `model_low_confidence` | confidence < 0.4 | Add similar examples to training data |
| `rule_parser_match` | Rule parser handled it | Track coverage ratio |
| `safety_validator_override` | Model confirm → validator forced ask | Debug model vs validator mismatch |
| `multi_txn_split` | "lunch ২০০, bus ১০০" detected | Track how often users multi-enter |
| `session_state_gap` | Model dropped known field | Fix session injection |
| `subcategory_raw` | Raw term extracted from Others input | Build term → category mapping |

### Retrain Trigger Rules
- Same `subcategory_raw` appears 10+ times → add to training data + suggest as new category
- `safety_validator_override` rate > 20% → model needs retraining
- `rule_parser_match` rate dropping → rules becoming obsolete

---

## 12. Architecture Truth

> এটা "AI model system" না  
> এটা **"deterministic financial parser with probabilistic extraction layer"**

Qwen 1.5B is NOT the brain. It's a pattern → JSON converter.  
The brain is your backend pipeline: rule parser → safety validator → executor.

### What Makes This Production-Grade
- LLM fails → pipeline catches it
- LLM hallucinates → validator rejects it
- LLM is slow → rule parser skips it
- LLM is uncertain → debug log captures it

### What Will Kill This Architecture

| Risk | Why | Fix |
|------|-----|-----|
| Rule parser grows too big | 6 months later it's a monster | Keep it minimal. Only exact/fixed patterns |
| Confidence over-relied | Model says 0.9 but wrong | Confidence = soft hint. Validator decides |
| "Others" unchecked | Analytics useless | Dynamic subcategory log + clustering |
| Backend becomes semantic | Rules start doing NLP | Backend = deterministic ONLY. No semantic expansion |
| No logging → no retraining | Blind to failure | Log every override, fallback, mismatch |
| Session state ignored | Long context drift | Inject session into system prompt, don't rely on attention |
| Thin note slips through | Audit trail useless | `is_note_sufficient()` in safety validator blocks thin notes |

---

## 13. Comparison: Old Plan vs Reality

| Aspect | Old (Over-Engineered) | New (Reality) |
|--------|----------------------|---------------|
| Schema depth | 4 levels nested | Flat, 1 level |
| Intents | 20 | 12 |
| State machine | Full FSM | Just message array |
| API generation | Model calls API | Backend calls API |
| Category | Strict enforce | Soft + backend validate |
| Multi-turn state | `known_fields` object | Context window |
| Date/amount | Model normalizes | Backend normalizes |
| Evaluation targets | 95%+ | 70-85% (realistic) |
| Banglish in data | 5% | 30-40% (critical for Qwen) |
| Training examples | 50,000 | 8,000 (enough for 1.5B) |
| Architecture | AI system | Deterministic parser + AI extractor |
| Confidence use | Decision gate | Soft hint only |
| Category handling | Strict enforce | Soft + dynamic subcategory log |
| Note handling | Optional field | THICK note required (3+ elements), AI pushes for detail |
| Session state | Model memory | Inject into system prompt |
| Debug tracing | none | Full debug field + event logging |
| Fallback tracking | none | Log all → cluster → retrain |

---

## 13. Quick Start (Today)

1. Open `AI Server/`
2. Create `dataset/` folder
3. Run template generator (Python script) → 500 examples
4. Validate JSON format
5. Convert to ChatML
6. LoRA fine-tune Qwen 1.5B with those 500
7. Test with 50 real inputs
8. Fix → add more → repeat

Don't wait for 8,000 examples. Start with 500, see how it behaves, then iterate.
