"""
Hisab Pata — Dataset Booster
Generates 3000+ extra examples to strengthen weak areas:
- Send (contact handling, Banglish, no-contact fallback)
- Edit / Delete / Approve / Reject
- Identity (name, creator questions)
- Income (Banglish, spelling)
- Expense (edge cases: zero, negative, very large, mixed units)
- Query variations (summary, list, balance)
"""

import json, random

random.seed(999)

CATEGORIES = ["Transport", "Mobile Recharge", "Postage", "Publication",
              "Office Stationery", "Tips", "Donation", "Others", "Salary"]
CATEGORIES_BN = {"Transport": "পরিবহন", "Mobile Recharge": "মোবাইল রিচার্জ",
                 "Postage": "ডাক", "Publication": "প্রকাশনা",
                 "Office Stationery": "অফিস স্টেশনারি", "Tips": "টিপস",
                 "Donation": "দান", "Others": "অন্যান্য", "Salary": "বেতন"}
AMOUNTS = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 1000, 1200,
           1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 8000, 10000, 15000,
           20000, 25000, 30000, 50000]
CONTACTS = ["রহিম", "করিম", "সুমন", "নাসরিন", "ফাতেমা", "জামাল", "সাজিদ",
            "তানিয়া", "রাহাত", "শাওন", "সাকিব", "নাঈম", "রাশেদ", "মিম",
            "অর্ণব", "প্রিয়তি", "Rahim", "Karim", "Tania", "Sakib"]

REASONS = ["অফিসের কাজে", "জরুরী কাজে", "বাজার করতে", "পরিবারের জন্য",
           "অসুস্থ বলে", "আত্মীয়ের বাড়িতে", "দাওয়াত খেতে", "ঘুরতে গিয়ে",
           "বন্ধুর জন্য", "হাঁটতে গিয়ে"]
LOCATIONS = ["পল্টন", "গুলশান", "ধানমন্ডি", "মিরপুর", "উত্তরা", "মোহাম্মদপুর",
             "নিউমার্কেট", "বসুন্ধরা", "বাসায়", "অফিসে", "ফার্মেসিতে",
             "হাসপাতালে", "স্কুলে", "রেস্টুরেন্টে"]

def sp():
    return f"book_type: personal\ncategories: {', '.join(CATEGORIES)}\nbalance: 12500"

def mk_note(cat=None):
    c = cat or random.choice([x for x in CATEGORIES if x != "Salary"])
    items = {
        "Transport": ["রিক্সা ভাড়া", "বাস ভাড়া", "উবার ভাড়া", "পেট্রোল", "সিএনজি"],
        "Mobile Recharge": ["মোবাইল রিচার্জ", "ফোন রিচার্জ", "ডেটা প্যাকেজ"],
        "Postage": ["কুরিয়ার খরচ", "পার্সেল পাঠানো", "ডাক খরচ"],
        "Publication": ["বই কেনা", "ম্যাগাজিন", "পাঠ্যবই"],
        "Office Stationery": ["কলম", "খাতা", "ফাইল", "স্টেশনারি"],
        "Tips": ["টিপস দেওয়া", "বখশিশ"],
        "Donation": ["দান করা", "সদকা", "মসজিদে দান"],
        "Others": ["লাঞ্চ", "ডিনার", "বাজার", "ওষুধ", "কাপড়"],
        "Salary": ["বেতন"],
    }
    item = random.choice(items.get(c, ["লাঞ্চ"]))
    r = random.choice(REASONS)
    l = random.choice(LOCATIONS)
    return random.choice([
        f"{r} {l} {item} বাবদ খরচ",
        f"{l} {r} {item}",
        f"{item} {l} {r} দেওয়া",
    ]), c

# ── Expense booster ──────────────────────────────────────────────────────
def gen_expense_varied():
    a = random.choice(AMOUNTS)
    note, cat = mk_note()
    user = random.choice([
        f"আজ {a} টাকা {note} করেছি",
        f"{a} টাকা {note} লাগলো",
        f"গতকাল {a} টাকা {note} দিলাম",
        f"আজকে {a} taka {note} khorch korsi",
        f"{a} টাকা খরচ {note}",
        f"একটা {a} টাকার খরচ {note}",
    ])
    asst = json.dumps({"intent":"expense","slots":{"amount":a,"category":cat,"note":note},"action":"confirm","missing_fields":[],"confidence":round(random.uniform(0.85,0.96),2)})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_expense_no_cat():
    a = random.choice(AMOUNTS[:15])
    user = random.choice([
        f"{a} টাকা খরচ করেছি, কী ক্যাটাগরি হবে?",
        f"আজ {a} টাকা খরচ করলাম — কোন ক্যাটাগরি দিব?",
        f"{a} taka khorch, category ta bolo",
        f"একটা {a} টাকার খরচ করে ফেলেছি",
    ])
    asst = json.dumps({"intent":"expense","slots":{"amount":a},"action":"ask","missing_fields":["category"],"question":"কিসের জন্য খরচ করছেন? কোন ক্যাটাগরিতে দেব?","confidence":0.65})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_expense_no_amount():
    cat = random.choice([x for x in CATEGORIES if x != "Salary"])
    cat_bn = CATEGORIES_BN[cat]
    user = random.choice([
        f"আজ {cat_bn} খরচ করেছি, কিন্তু কত টাকা ভুলে গেছি",
        f"{cat_bn} ক্যাটাগরিতে একটা খরচ আছে — টাকা মনে নাই",
        f"ekta {cat_bn} khorch hoyeche, koto taka bhule gesi",
    ])
    asst = json.dumps({"intent":"expense","slots":{},"action":"ask","missing_fields":["amount","note"],"question":"কত টাকা খরচ করছেন? বিস্তারিত জানান।","confidence":0.55})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Income booster ───────────────────────────────────────────────────────
def gen_income_varied():
    a = random.choice([5000, 8000, 10000, 12000, 15000, 20000, 25000, 30000, 35000, 40000, 50000])
    sources_bn = [f"{a} টাকা বেতন পেয়েছি", f"{a} টাকা সেলারি এসেছে",
                  f"{a} টাকা মাইনে পেলাম", f"{a} টাকা ইনকাম বেতন বাবদ"]
    sources_bl = [f"salary paichi {a} taka", f"{a} taka income salary theke",
                  f"bheton esheche {a} taka", f"maine paisi {a} taka"]
    user = random.choice(sources_bn + sources_bl)
    asst = json.dumps({"intent":"income","slots":{"amount":a,"category":"Salary","note":"বেতন বাবদ ইনকাম"},"action":"confirm","missing_fields":[],"confidence":0.92})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_income_other():
    a = random.choice([2000, 3000, 5000, 8000, 10000, 15000])
    src = random.choice(["ফ্রিল্যান্সিং", "টিউশনি", "বিক্রয়", "বাড়ি ভাড়া", "কমিশন", "bonus"])
    user = random.choice([
        f"{src} থেকে {a} টাকা পেয়েছি",
        f"{a} টাকা {src} করে ইনকাম",
        f"{src} theke {a} taka income",
        f"{a} taka {src} income",
    ])
    asst = json.dumps({"intent":"income","slots":{"amount":a,"category":"Others","note":f"{src} থেকে ইনকাম"},"action":"confirm","missing_fields":[],"confidence":0.88})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Send booster ─────────────────────────────────────────────────────────
def gen_send_varied():
    a = random.choice([200, 300, 500, 1000, 1500, 2000, 3000, 5000])
    c = random.choice(CONTACTS)
    user = random.choice([
        f"{c} কে {a} টাকা সেন্ড করেছি",
        f"{c} ke {a} send korsi",
        f"{c} কে {a} টাকা পাঠিয়েছি",
        f"{c} er kase {a} taka pathaisi",
        f"send korechi {a} taka {c} ke",
        f"{c} k {a} tk send",
    ])
    asst = json.dumps({"intent":"send","slots":{"amount":a,"category":"Send","contact":c,"note":f"{c} কে সেন্ড"},"action":"confirm","missing_fields":[],"confidence":0.92})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_send_no_contact():
    a = random.choice([200, 500, 1000])
    user = random.choice([
        f"{a} টাকা সেন্ড করেছি (কার কাছে বলতে ভুলে গেছি)",
        f"{a} taka send korsi — ke paise mone nai",
        f"ekjonke {a} টাকা send করলাম",
        f"সেন্ড করেছি {a} টাকা — নামটা বলুন",
    ])
    asst = json.dumps({"intent":"send","slots":{"amount":a,"category":"Send"},"action":"ask","missing_fields":["contact"],"question":"কার কাছে টাকা পাঠিয়েছেন? নাম জানান।","confidence":0.65})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Edit / Delete / Approve / Reject booster ─────────────────────────────
def gen_edit_varied():
    old = random.choice([100, 200, 300, 500, 1000, 1500])
    new = old + random.choice([50, 100, -50, -100, 200, -200])
    user = random.choice([
        f"গত {old} টাকার এন্ট্রিটা {new} করে দিন",
        f"{old} টাকা থেকে {new} টাকা change করো",
        f"oii {old} taka ta {new} kore din",
        f"last entry amount change: {old}→{new}",
        f"ভুল হয়ে গেছে — {old} টাকাটা {new} হবে",
    ])
    asst = json.dumps({"intent":"edit","slots":{"amount":new},"action":"confirm","missing_fields":[],"confidence":0.82})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_delete_varied():
    user = random.choice([
        "লাস্ট এন্ট্রিটা মুছে ফেলো",
        "delete koro last ta", "শেষ টা বাদ দাও",
        "গতকালের এন্ট্রি ডিলিট করো",
        "remove koro last entry ta",
        "সব শেষ করে দাও",
    ])
    asst = json.dumps({"intent":"delete","slots":{},"action":"confirm","missing_fields":[],"confidence":0.85})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_approve_varied():
    user = random.choice([
        "হ্যাঁ, ঠিক আছে", "approve koro", "হ্যাঁ অ্যাপ্রুভ করো",
        "ঠিক আছে, confirm", "ok approve", "হ্যাঁ করো",
        "বেশ, approve দাও", "ok kore dao",
    ])
    asst = json.dumps({"intent":"approve","slots":{},"action":"confirm","missing_fields":[],"confidence":0.90})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_reject_varied():
    user = random.choice([
        "না, বাতিল করো", "না ঠিক নেই", "reject koro",
        "না, cancel", "বাতিল", "ঠিক না, বাদ দাও",
        "না, হবে না", "reject", "না",
    ])
    asst = json.dumps({"intent":"reject","slots":{},"action":"confirm","missing_fields":[],"confidence":0.88})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Identity booster ─────────────────────────────────────────────────────
def gen_identity_varied():
    user = random.choice([
        "তোমার নাম কী?", "কে তুমি?", "তোমার পরিচয়?",
        "who are you?", "what is your name?",
        "কে বানিয়েছে তোমাকে?", "তোমার ডেভেলপার কে?",
        "তুমি কার তৈরি?", "তোমার creator কে?",
        "তুমি Hisab AI?", "name ta ki?",
        "আপনার নাম কী?", "কে তোমাকে বানিয়েছে?",
    ])
    responses = [
        "আমি Hisab AI — M Rahat বানিয়েছেন। আপনার ফাইন্যান্স সহায়ক।",
        "Hisab AI বলতে আমিই। ডেভেলপার: M Rahat। আপনার খরচ-ইনকাম ট্র্যাক করি।",
        "আমার নাম Hisab AI। বানিয়েছেন M Rahat। কী সাহায্য দরকার?",
        "Hisab AI, M Rahat-এর তৈরি। আপনি কী করতে চান?",
    ]
    asst = json.dumps({"intent":"help","slots":{},"action":"greeting","response":random.choice(responses),"missing_fields":[],"confidence":1.0})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_greeting_identity():
    """User greets → AI introduces self with name + creator."""
    user = random.choice(["হ্যালো", "হাই", "আসসালামু আলাইকুম", "hello", "শুরু করি"])
    responses = [
        "হ্যালো! আমি Hisab AI — M Rahat বানিয়েছেন। বলুন কী করতে চান?",
        "হাই! Hisab AI এ কথা বলছি। আপনার খরচ-ইনকাম জানান।",
        "ওয়ালাইকুম আসসালাম! Hisab AI এ স্বাগতম। কী সাহায্য দরকার?",
    ]
    asst = json.dumps({"intent":"greeting","slots":{},"action":"greeting","response":random.choice(responses),"missing_fields":[],"confidence":1.0})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_help_varied():
    user = random.choice([
        "তুমি কী করতে পারো?", "help", "features কী কী?",
        "what can you do?", "তোমার কাজ কী?",
        "কিভাবে ব্যবহার করব?", "guide me",
        "তোমার ফিচার কি কি?",
    ])
    responses = [
        "আমি খরচ ও ইনকাম ট্র্যাক করি, ব্যালেন্স দেখাই, লেনদেন লিস্ট দিই। শুধু বলুন '৫০০ টাকা খরচ' বা 'বেতন এসেছে' — বাকি আমি দেখব।",
        "Hisab AI আপনার ফাইন্যান্স সহায়ক। খরচ যোগ করুন, ইনকাম যোগ করুন, ব্যালেন্স চেক করুন — সব বাংলায়।",
    ]
    asst = json.dumps({"intent":"help","slots":{},"action":"greeting","response":random.choice(responses),"missing_fields":[],"confidence":1.0})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Query booster ────────────────────────────────────────────────────────
def gen_balance_varied():
    user = random.choice([
        "ব্যালেন্স কত?", "কত টাকা আছে?", "আমার ব্যালেন্স দেখাও",
        "balance koto?", "current balance", "কত বাকি আছে?",
        "হাতে কত টাকা?", "আমার কাছে কত আছে?",
    ])
    asst = json.dumps({"intent":"balance","slots":{},"action":"confirm","missing_fields":[],"confidence":0.95})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_summary_varied():
    user = random.choice([
        "এই মাসের সারসংক্ষেপ দাও",
        "মাস শেষে ইনকাম-খরচ দেখাও",
        "summary report",
        "এই মাসে কত খরচ করলাম?",
        "monthly summary দাও",
        "গত মাসের রিপোর্ট চাই",
        "আয়-ব্যয়ের বিবরণ দাও",
    ])
    asst = json.dumps({"intent":"summary","slots":{},"action":"confirm","missing_fields":[],"confidence":0.90})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

def gen_list_varied():
    user = random.choice([
        "গত ৭ দিনের লেনদেন দেখাও",
        "আজকের লেনদেনের তালিকা",
        "transaction list",
        "সব লেনদেন দেখাও",
        "list of recent transactions",
        "এই সপ্তাহের লেনদেন",
    ])
    asst = json.dumps({"intent":"list","slots":{},"action":"confirm","missing_fields":[],"confidence":0.90})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

# ── Goodbye / Thanks booster ─────────────────────────────────────────────
def gen_goodbye_varied():
    user = random.choice([
        "বাই", "bye", "আচ্ছা যাই", "ধন্যবাদ", "thanks",
        "ঠিক আছে, আসি", "পরে কথা হবে", "thank you",
    ])
    responses = [
        "ধন্যবাদ! Hisab AI ব্যবহার করার জন্য। আবার আসবেন।",
        "বাই! আপনার দিন শুভ হোক।",
        "আপনাকেও ধন্যবাদ! Hisab AI সবসময় প্রস্তুত।",
    ]
    asst = json.dumps({"intent":"greeting","slots":{},"action":"greeting","response":random.choice(responses),"missing_fields":[],"confidence":1.0})
    return {"messages":[{"role":"system","content":sp()},{"role":"user","content":user},{"role":"assistant","content":asst}]}

GENERATORS = {
    "expense_varied": (gen_expense_varied, 400),
    "expense_no_cat": (gen_expense_no_cat, 80),
    "expense_no_amount": (gen_expense_no_amount, 50),
    "income_varied": (gen_income_varied, 150),
    "income_other": (gen_income_other, 80),
    "send_varied": (gen_send_varied, 200),
    "send_no_contact": (gen_send_no_contact, 60),
    "edit_varied": (gen_edit_varied, 100),
    "delete_varied": (gen_delete_varied, 60),
    "approve_varied": (gen_approve_varied, 40),
    "reject_varied": (gen_reject_varied, 40),
    "identity_varied": (gen_identity_varied, 100),
    "greeting_identity": (gen_greeting_identity, 80),
    "help_varied": (gen_help_varied, 50),
    "balance_varied": (gen_balance_varied, 60),
    "summary_varied": (gen_summary_varied, 50),
    "list_varied": (gen_list_varied, 50),
    "goodbye_varied": (gen_goodbye_varied, 40),
}

def main():
    all_examples = []
    for name, (gen_fn, count) in GENERATORS.items():
        for i in range(count):
            try:
                all_examples.append(gen_fn())
            except Exception as e:
                print(f"Error {name}#{i}: {e}")

    random.shuffle(all_examples)

    path = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw/booster.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Booster generated: {len(all_examples)}")

    # Count intents
    intents = {}
    for ex in all_examples:
        for m in ex["messages"]:
            if m["role"] == "assistant":
                try:
                    i = json.loads(m["content"]).get("intent", "?")
                    intents[i] = intents.get(i, 0) + 1
                except:
                    pass
    print("Intents:", dict(sorted(intents.items(), key=lambda x: -x[1])))

    # Show sample
    print("\nSample:")
    ex = random.choice(all_examples)
    user_msg = [m for m in ex["messages"] if m["role"] == "user"][0]["content"]
    asst = [m for m in ex["messages"] if m["role"] == "assistant"][0]["content"]
    print(f"  U: {user_msg}")
    print(f"  AI: {asst[:100]}")

if __name__ == "__main__":
    main()
