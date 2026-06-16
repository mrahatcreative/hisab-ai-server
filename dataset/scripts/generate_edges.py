"""
Hisab Pata — Edge Case Generator (Phase 3)
Generates tricky inputs: zero amounts, missing fields, vague queries, unknown categories
"""

import json, random

random.seed(42)

AMOUNTS = [50, 100, 200, 300, 500, 1000, 2000, 5000]
CATEGORIES = ["Transport", "Mobile Recharge", "Others", "Salary"]

def system_prompt():
    return f"book_type: personal\ncategories: {', '.join(CATEGORIES)}\nbalance: 12500"

# ── Zero / Negative ─────────────────────────────────────────────────────────
def gen_zero_amount():
    user = random.choice(["আজ ০ টাকা খরচ করেছি", "0 টাকা lunch", "আজ টাকা খরচ করিনি"])
    asst = json.dumps({"intent":"expense","slots":{"amount":0},"action":"ask","missing_fields":["amount"],"question":"পরিমাণ কি ঠিক আছে? ০ টাকা লাগতে পারে না।","confidence":0.3}, ensure_ascii=False)
    return {"messages":[{"role":"system","content":system_prompt()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_negative_amount():
    user = random.choice(["-৫০০ টাকা খরচ", "-200 taka", "মাইনাস ৩০০ টাকা"])
    asst = json.dumps({"intent":"expense","slots":{"amount":-500},"action":"ask","missing_fields":["amount"],"question":"ঋণাত্মক টাকা হয় না। কত টাকা খরচ করছেন?","confidence":0.25}, ensure_ascii=False)
    return {"messages":[{"role":"system","content":system_prompt()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Unknown category ────────────────────────────────────────────────────────
def gen_unknown_category():
    terms = ["নেটফ্লিক্স", "স্পটিফাই", "উবার", "ফুডপান্ডা", "স্টার্টআপ", "গেমিং", "ইউটিউব প্রিমিয়াম"]
    term = random.choice(terms)
    amount = random.choice(AMOUNTS)
    user = random.choice([f"আজ {amount} টাকা {term} দিয়েছি", f"{amount} taka {term} khorch"])
    asst = json.dumps({"intent":"expense","slots":{"amount":amount,"category":"Others","note":f"{term}"},"action":"confirm","missing_fields":[],"confidence":0.7}, ensure_ascii=False)
    return {"messages":[{"role":"system","content":system_prompt()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Vague / Ambiguous ───────────────────────────────────────────────────────
def gen_vague():
    inputs = [
        "টাকা খরচ করেছি", "কিছু টাকা খরচ করেছি", "আজ খরচ করেছি",
        "khorch korsi", "ektu taka khorch",
    ]
    user = random.choice(inputs)
    asst = json.dumps({"intent":"expense","slots":{},"action":"ask","missing_fields":["amount","category"],"question":"কত টাকা এবং কিসের জন্য খরচ করছেন?","confidence":0.3}, ensure_ascii=False)
    return {"messages":[{"role":"system","content":system_prompt()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_pure_greeting():
    user = random.choice(["হ্যালো", "হাই", "hello", "hi", "আসসালামু আলাইকুম", "সালাম"])
    responses = [
        "আসসালামু আলাইকুম! Hisab AI এ স্বাগতম। কী সাহায্য দরকার?",
        "হ্যালো! Hisab AI এ কথা বলছি। কী করবেন?",
        "হাই, Hisab AI এ কথা বলুন।",
    ]
    asst = json.dumps({"intent":"greeting","slots":{},"action":"greeting","response":random.choice(responses),"missing_fields":[],"confidence":1.0}, ensure_ascii=False)
    return {"messages":[{"role":"system","content":system_prompt()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_chitchat():
    user = random.choice(["আজ আবহাওয়া কেমন?", "তুমি কেমন আছো?", "what's up?", "খবর কি?", "ভালো আছো?"])
    responses = [
        "আমি Hisab AI, সবসময় প্রস্তুত! আপনার খরচ-ইনকাম নিয়ে বলুন।",
        "ভালো আছি! আপনার ফাইন্যান্স ট্র্যাক করতে রেডি। কী করবেন?",
    ]
    asst = json.dumps({"intent":"help","slots":{},"action":"greeting","response":random.choice(responses),"missing_fields":[],"confidence":1.0}, ensure_ascii=False)
    return {"messages":[{"role":"system","content":system_prompt()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── All generators ──────────────────────────────────────────────────────────
GENERATORS = [
    (gen_zero_amount, 30),
    (gen_negative_amount, 20),
    (gen_unknown_category, 80),
    (gen_vague, 60),
    (gen_pure_greeting, 20),
    (gen_chitchat, 20),
]

def main():
    all_examples = []
    for fn, count in GENERATORS:
        for i in range(count):
            all_examples.append(fn())
    random.shuffle(all_examples)
    print(f"Edge cases generated: {len(all_examples)}")

    path = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw/edge_cases.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Saved to: {path}")

if __name__ == "__main__":
    main()
