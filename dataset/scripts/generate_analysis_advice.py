"""
Hisab Pata — Natural Conversation, Analysis & Advice Dataset
Completely rewritten for natural feel — no robotic patterns.
"""

import json, random

random.seed(777)

CATEGORIES_BN = {
    "Transport": "পরিবহন", "Mobile Recharge": "মোবাইল রিচার্জ",
    "Postage": "ডাক", "Publication": "প্রকাশনা",
    "Office Stationery": "অফিস স্টেশনারি", "Tips": "টিপস",
    "Donation": "দান", "Others": "অন্যান্য", "Salary": "বেতন"
}
CATEGORIES_EN = list(CATEGORIES_BN.keys())

AMOUNTS = [200, 500, 800, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 8000, 10000, 12000, 15000, 20000, 25000, 30000]
INCOME_AMOUNTS = [15000, 20000, 25000, 30000, 35000, 40000, 50000]
BALANCES = [1200, 3500, 8500, 12500, 20000, 50000, 100000]

def system_prompt(balance=12500, categories=None):
    cats = ", ".join(categories or CATEGORIES_EN)
    return f"book_type: personal\ncategories: {cats}\nbalance: {balance}"

def fake_context(balance=None):
    b = balance or random.choice(BALANCES)
    recent = []
    for _ in range(random.randint(3, 5)):
        cat = random.choice(CATEGORIES_EN[:-1])
        recent.append({"amount": random.choice(AMOUNTS), "category": cat, "type": "expense", "note": ""})
    recent.append({"amount": random.choice(INCOME_AMOUNTS), "category": "Salary", "type": "income", "note": "বেতন"})
    random.shuffle(recent)
    return {"balance": b, "recent": recent}

def top_category(recent):
    spending = {}
    for t in recent:
        if t.get("type") == "expense":
            cat = t["category"]
            spending[cat] = spending.get(cat, 0) + t.get("amount", 0)
    if not spending:
        return ("Others", 0)
    return max(spending.items(), key=lambda x: x[1])

def category_totals(recent):
    spending = {}
    for t in recent:
        cat = t["category"]
        spending[cat] = spending.get(cat, 0) + t.get("amount", 0)
    return spending

def total_expense(recent):
    return sum(t.get("amount", 0) for t in recent if t.get("type") == "expense")

def total_income(recent):
    return sum(t.get("amount", 0) for t in recent if t.get("type") == "income")

# ── Colloquial helpers ─────────────────────────────────────────────────────
OK_BANGLA = ["আচ্ছা", "ঠিক আছে", "ধরুন", "দেখুন", "জ্বি", "হ্যাঁ", "ওকে"]
FILLERS = ["মানে", "আসলে", "তো", "আচ্ছা", "দেখুন", "জ্বি"]
STARTERS = {
    "analysis": [
        "দেখি আপনার ডাটা থেকে কি বলতে পারি...",
        "এইবারের রিপোর্ট বলছে—",
        "আপনার খরচের প্যাটার্ন দেখে বলছি:",
        "জ্বি, দেখি একটু...",
        "হ্যাঁ, আপনার ডাটায় দেখা যাচ্ছে—",
        "আচ্ছা, আপনার খরচগুলো দেখি...",
        "ক্যালকুলেশন করে বলছি:",
        "",
        "",
    ],
    "advice": [
        "আমার মতে—",
        "ছোট একটা পরামর্শ দিতে পারি?",
        "জ্বি, বলছি—",
        "হ্যাঁ, এই ব্যাপারে আমার কিছু বলার আছে—",
        "আচ্ছা, শুনুন—",
        "আমি যা বুঝি: ",
        "",
        "",
    ],
}

def user_cat_q(cat_bn):
    """Natural user questions about a category."""
    return random.choice([
        f"আচ্ছা, {cat_bn} খাতে কত খরচ করছি এই মাসে?",
        f"{cat_bn} খরচ কেমন হচ্ছে বলো তো?",
        f"এই মাসে {cat_bn} ক্যাটাগরিতে কত দিলাম?",
        f"{cat_bn} খাতে কত টাকা গেছে?",
        f"আমার {cat_bn} এর খরচটা কেমন?",
        f"{cat_bn} ক্যাটাগরির হিসাব দাও",
        f"{cat_bn} তে কত খরচ হলো বলবেন?",
        f"এই মাসের {cat_bn} ট্র্যাক করো",
    ])

# ── Analysis generators ────────────────────────────────────────────────────

def gen_natural_top_category():
    ctx = fake_context()
    top_cat, top_amount = top_category(ctx["recent"])
    top_bn = CATEGORIES_BN.get(top_cat, top_cat)

    user = random.choice([
        "আমার সবচেয়ে বেশি খরচ কোন খাতে হচ্ছে?",
        "কোন জিনিসে বেশি টাকা দিচ্ছি বলো?",
        "সবচেয়ে বড় খরচের খাত কোনটা?",
        "কোন ক্যাটাগরিতে সবচেয়ে বেশি খরচ হলো?",
        "বলো তো, আমি সবচেয়ে বেশি কীসে খরচ করি?",
        "এই মাসে কোন খাতে সবচেয়ে বেশি টাকা দিয়েছি?",
    ])

    responses = [
        f"সবচেয়ে বেশি খরচ কিন্তু **{top_bn}** খাতে — মোট **{top_amount:,} টাকা**। বাকিগুলো তারচেয়ে কম।",
        f"আপনার {'পরিবহন' if top_cat != 'Transport' else 'ট্রান্সপোর্ট'} এর চেয়ে **{top_bn}** খরচ বেশি — {top_amount:,} টাকা! এই খাতে একটু নজর দিলে ভালো হয়।",
        f"**{top_bn}** সবার ওপরে — {top_amount:,} টাকা। ব্যস, এইটা আপনার মাসের সবচেয়ে বড় খরচের খাত।",
        f"গণনা করে দেখলাম, **{top_bn}**-তেই সবচেয়ে বেশি টাকা গিয়েছে: {top_amount:,} টাকা।",
    ]

    assistant = json.dumps({
        "intent": "analysis", "slots": {"category": top_cat, "amount": top_amount},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(balance=ctx["balance"])},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_breakdown():
    ctx = fake_context()
    spending = category_totals(ctx["recent"])
    sorted_cats = sorted(spending.items(), key=lambda x: -x[1])[:4]

    user = random.choice([
        "কোন ক্যাটাগরিতে কত খরচ করছি, একটা লিস্ট দাও",
        "ক্যাটাগরি ওয়াইজ খরচ দেখাও প্লিজ",
        "আমার খরচগুলো ক্যাটাগরি ধরে ধরে বলো",
        "ডিটেইলস চাই — কোন খাতে কত টাকা গেল?",
        "বলো তো কোন খাতে কী পরিমাণ খরচ করেছি",
    ])

    lines = [f"{CATEGORIES_BN.get(c, c)} — {a:,} টাকা" for c, a in sorted_cats]
    top_bn = CATEGORIES_BN.get(sorted_cats[0][0], sorted_cats[0][0])

    responses = [
        "এই নিন আপনার খরচ:\n" + "\n".join(lines) + f"\n\nমনে রাখবেন, **{top_bn}**-তেই সবচেয়ে বেশি যাচ্ছে।",
        "ক্যাটাগরি অনুযায়ী:\n" + "\n".join(lines) + f"\n\nসবচেয়ে বেশি কিন্তু {top_bn} খাতে।",
        "\n".join(lines) + f"\n\nসবমিলিয়ে সবচেয়ে বড় খাত {top_bn}। বাকিগুলো কমবেশি।",
    ]

    assistant = json.dumps({
        "intent": "analysis", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(balance=ctx["balance"])},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_monthly():
    ctx = fake_context()
    total_exp = total_expense(ctx["recent"])
    total_inc = total_income(ctx["recent"])
    top_cat, top_amt = top_category(ctx["recent"])
    top_bn = CATEGORIES_BN.get(top_cat, top_cat)
    bal = ctx["balance"]
    save = total_inc - total_exp

    user = random.choice([
        "এই মাসের মতো কী হলো?",
        "গত মাসের একটু সারসংক্ষেপ দাও",
        "আমার এই মাসের আয়-ব্যয় কেমন?",
        "মাস শেষ, একটা রিপোর্ট চাই",
        "বলো তো এই মাসে কত খরচ আর কত ইনকাম?",
        "মাসের হিসাবটা দেখাও",
    ])

    responses = []
    if save > 0:
        responses.append(
            f"এই মাসে আয় হয়েছে **{total_inc:,} টাকা**, খরচ **{total_exp:,} টাকা**।\n"
            f"সেভ করেছেন **{save:,} টাকা** — ভালো! 🎉\n"
            f"সবচেয়ে বেশি খরচ {top_bn} খাতে ({top_amt:,} টাকা)।\n"
            f"হাতে এখন {bal:,} টাকা আছে।"
        )
        responses.append(
            f"গত মাস আপনি শেষ করেছেন {bal:,} টাকা হাতে রেখে।\n"
            f"মোট ইনকাম ছিল {total_inc:,} টাকা, আর খরচ {total_exp:,} টাকা।\n"
            f"বেশি খরচ হয়েছে {top_bn}-এ — {top_amt:,} টাকা।\n"
            f"বাকি মাসের জন্য {save:,} টাকা সঞ্চয়! দারুণ ব্যাপার।"
        )
    else:
        responses.append(
            f"এই মাসে খরচ বেশি হয়েছে কিছুটা।\n"
            f"আয় {total_inc:,} টাকা, খরচ {total_exp:,} টাকা।\n"
            f"{top_bn} খাতে সবচেয়ে বেশি খরচ — {top_amt:,} টাকা।\n"
            f"আগামী মাসে {top_bn} খাতে একটু কমানোর চেষ্টা করলে ভালো হবে।"
        )
        responses.append(
            f"এই মাসের হিসাব: আয় {total_inc:,} টাকা, খরচ {total_exp:,} টাকা।\n"
            f"সবচেয়ে বড় খরচ {top_bn}-এ — {top_amt:,} টাকা।\n"
            f"হাতে আছে {bal:,} টাকা। পরের মাসে খেয়াল রাখবেন।"
        )

    assistant = json.dumps({
        "intent": "analysis", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(balance=bal)},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_compare():
    ctx = fake_context()
    spending = category_totals(ctx["recent"])
    cats = [c for c in spending if c != "Salary"]
    if len(cats) < 2:
        cats = ["Transport", "Others"]
    cat1, cat2 = random.sample(cats, 2)
    amt1 = spending.get(cat1, random.choice(AMOUNTS))
    amt2 = spending.get(cat2, random.choice(AMOUNTS))
    bn1 = CATEGORIES_BN.get(cat1, cat1)
    bn2 = CATEGORIES_BN.get(cat2, cat2)

    user = random.choice([
        f"{bn1} আর {bn2} এর খরচের তুলনা দাও",
        f"কোন খাতে বেশি খরচ হচ্ছে — {bn1} না {bn2}?",
        f"{bn1} বনাম {bn2} — কোনটায় বেশি টাকা গেল?",
        f"তুলনা করো {bn1} আর {bn2} এর খরচ",
    ])

    if amt1 > amt2:
        diff = amt1 - amt2
        responses = [
            f"{bn1} খাতে {amt1:,} টাকা, আর {bn2} খাতে {amt2:,} টাকা।\n{bn1}-এ {diff:,} টাকা বেশি।",
            f"{bn1}: {amt1:,} টাকা | {bn2}: {amt2:,} টাকা\nঅর্থাৎ {bn1} বেশি {diff:,} টাকা।",
        ]
    else:
        diff = amt2 - amt1
        responses = [
            f"{bn2} খাতে {amt2:,} টাকা, আর {bn1} খাতে {amt1:,} টাকা।\n{bn2}-এ {diff:,} টাকা বেশি।",
            f"{bn2}: {amt2:,} টাকা | {bn1}: {amt1:,} টাকা\nপার্থক্য {diff:,} টাকা — {bn2} বেশি।",
        ]

    assistant = json.dumps({
        "intent": "analysis", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.80, 0.92), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(balance=ctx["balance"])},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_specific_cat():
    cat = random.choice(CATEGORIES_EN[:-1])
    bn = CATEGORIES_BN.get(cat, cat)
    ctx = fake_context()
    amount = ctx["recent"][0].get("amount", random.choice(AMOUNTS))

    user = user_cat_q(bn)

    responses = [
        f"এই মাসে {bn} খাতে খরচ হয়েছে **{amount:,} টাকা**।",
        f"{bn} ক্যাটাগরিতে এখন পর্যন্ত {amount:,} টাকা দিয়েছেন।",
        f"হ্যাঁ, {bn} খাতে {amount:,} টাকা গিয়েছে এই মাসে।",
        f"{amount:,} টাকা — এইটা আপনার {bn} খরচ এই মাসে।",
    ]

    assistant = json.dumps({
        "intent": "analysis", "slots": {"category": cat, "amount": amount},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(balance=ctx["balance"])},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Advice generators ──────────────────────────────────────────────────────

def gen_natural_save_tips():
    user = random.choice([
        "টাকা বাঁচানোর কোনো উপায় বলো?",
        "কিছু টাকা জমাতে চাই, কী করব?",  
        "খরচ কমানোর টিপস দাও প্লিজ",
        "আমি কিভাবে বেশি সেভ করতে পারি?",
        "টাকা জমানোর উপায় কী?",
        "বাঁচানোর টিপস দাও",
        "খরচ কমাবো কীভাবে?",
    ])

    all_tips = [
        ("প্রতি মাসে আয়ের ১০% আলাদা রাখুন — আগে সেভ, তারপর খরচ", "দারুণ একটা টিপস"),
        ("বাজার করতে যাওয়ার আগে লিস্ট বানান, দেখবেন ২০% কম খরচ হয়", "ট্রাই করতে পারেন"),
        ("রেস্টুরেন্টের চেয়ে বাসায় রান্না করলে মাসে হাজার খানেক বাঁচে", "সত্যি কথা"),
        ("যে সাবস্ক্রিপশনগুলো লাগে না, সেগুলো বন্ধ করে দিন", "ছোট হিসাব বড় লাভ"),
        ("প্রতি সপ্তাহে একদিন 'কিছু না কেনার দিন' রাখুন", "মজার কিন্তু কার্যকর"),
        ("ক্যাশ ব্যাক আর ডিসকাউন্ট অফার ইউজ করুন — বড় কেনাকাটায় ৫-১০% সাশ্রয়", "ব্যবহারিক টিপস"),
        ("নগদ না রেখে আলাদা সেভিংস অ্যাকাউন্টে টাকা রাখুন", "নিরাপদ"),
        ("প্রতিদিনের খরচ নোট করুন। যেখানে টাকা যাচ্ছে দেখলেই নিয়ন্ত্রণে আসবে", "গুরুত্বপূর্ণ"),
    ]

    selected = random.sample(all_tips, random.randint(2, 4))
    tip_lines = [f"• {t[0]}" for t in selected]

    responses = [
        "আপনার জন্য কিছু টিপস:\n" + "\n".join(tip_lines),
        "আমি যা বলব:\n" + "\n".join(tip_lines),
        "খরচ কমানো খুব কঠিন না। একটু সচেতন হলেই হয়:\n" + "\n".join(tip_lines),
        "বলছি:\n" + "\n".join(tip_lines),
    ]

    assistant = json.dumps({
        "intent": "advice", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.85, 0.96), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_cat_advice():
    cat, tips = random.choice([
        ("Transport", [
            "অল্প দূরত্বে উবার না নিয়ে হাঁটুন — স্বাস্থ্যেও ভালো, টাকাও বাঁচে",
            "মাসিক বাস পাস নিলে ২০-৩০% সাশ্রয় হয়",
            "অফিসের জন্য কারপুল বা শাটল দেখতে পারেন",
        ]),
        ("Mobile Recharge", [
            "দীর্ঘমেয়াদী প্যাকেজ নিন, সস্তা পড়ে",
            "অপ্রয়োজনীয় অ্যাপের ডেটা বন্ধ রাখুন",
            "বাসায় ওয়াইফাই থাকলে মোবাইল ডেটা কম কিনলেই চলে",
        ]),
        ("Publication", [
            "লাইব্রেরি থেকে বই পড়তে পারেন — খরচ বাঁচে",
            "ই-বুক বা সেকেন্ডহ্যান্ড বই কিনলে অনেক সস্তা",
            "ম্যাগাজিনের বদলে অনলাইনে আর্টিকেল পড়ুন",
        ]),
        ("Donation", [
            "পরিকল্পিতভাবে দান করুন — নির্দিষ্ট একটা পরিমাণ ঠিক করে রাখুন",
            "ছোট ছোট দানে বড় সওয়াব, কিন্তু অযথা যেন না হয় খেয়াল রাখবেন",
        ]),
        ("Office Stationery", [
            "প্রয়োজনের বেশি কলম-খাতা না কেনাই ভালো",
            "অফিসের জিনিস বাড়িতে ব্যবহার না করলে খরচ কমবে",
        ]),
        ("Others", [
            "বাইরে খাওয়া কমিয়ে বাসায় খান — মাসে হাজার দুয়েক বাঁচবে",
            "কেনাকাটায় ইম্পালস কন্ট্রোল করুন — সত্যিই দরকার কি না ভাবুন",
            "সেল আর ডিসকাউন্টের সময়ে কেনাকাটা করলে টাকা বাঁচে",
        ]),
    ])

    bn = CATEGORIES_BN.get(cat, cat)
    user = random.choice([
        f"{bn} খরচ কীভাবে কমানো যায়?",
        f"{bn} ক্যাটাগরিতে বেশি খরচ হচ্ছে, কী করব?",
        f"{bn} খাতে টাকা বাঁচানোর উপায় বলো",
        f"{bn}-এ খরচ নিয়ন্ত্রণের টিপস দাও",
    ])

    responses = [
        f"{bn} খরচ কমানোর জন্য:\n" + "\n".join(f"• {t}" for t in random.sample(tips, min(2, len(tips)))),
        f"এই ক্যাটাগরির জন্য আমার পরামর্শ:\n" + "\n".join(f"• {t}" for t in random.sample(tips, min(2, len(tips)))),
        "\n".join(f"• {t}" for t in random.sample(tips, min(2, len(tips)))),
    ]

    assistant = json.dumps({
        "intent": "advice", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_budget():
    user = random.choice([
        "একটা বাজেট বানিয়ে দাও আমার জন্য",
        "মাসিক বাজেট কেমন হওয়া উচিত?",
        "বাজেট বানানোর নিয়ম কী?",
        "কিভাবে বুঝব কতটা বাজেট রাখব প্রত্যেক খাতে?",
        "বাজেটিং শেখাও",
    ])

    responses = [
        "সাধারণ একটা নিয়ম — আয়কে তিন ভাগে ভাগ করুন:\n"
        "• ৫০% — জরুরি খরচ (ভাড়া, বাজার, বিল)\n"
        "• ৩০% — ফ্রি খরচ (শপিং, বাইরে খাওয়া)\n"
        "• ২০% — সঞ্চয়\n\n"
        "আপনার আয় অনুযায়ী অ্যাডজাস্ট করে নেবেন। মাস শেষে হিসাব মিলিয়ে দেখুন।",
        "বাজেটের জন্য ৫০-৩০-২০ রুল ইউজ করতে পারেন:\n\n"
        "৫০% জরুরি প্রয়োজনে\n"
        "৩০% ফ্রি খরচে\n"
        "২০% সেভিংসে\n\n"
        "আপনার জন্য হিসাব করে দিতে পারলে জানাবেন।",
    ]

    assistant = json.dumps({
        "intent": "advice", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_emergency():
    user = random.choice([
        "জরুরি অবস্থার জন্য কত টাকা রাখা উচিত?",
        "এমারজেন্সি ফান্ড কত হওয়া দরকার?",
        "ইমারজেন্সির জন্য কীভাবে টাকা জমাব?",
        "হঠাৎ করে সমস্যায় পড়লে কত টাকা লাগতে পারে?",
    ])

    responses = [
        "ইমারজেন্সি ফান্ড হিসেবে ৩ থেকে ৬ মাসের খরচের সমান টাকা রাখা ভালো।\n\n"
        "ছোট করে শুরু করতে পারেন — প্রতি মাসে ১০০০ টাকা করে জমালেই ১ বছরে ১২ হাজার হয়ে যাবে।",
        "আমার মতে — ৩ মাসের মোট খরচের সমান টাকা ইমারজেন্সি ফান্ডে রাখবেন।\n\n"
        "এই টাকা আলাদা জায়গায় রাখুন, যাতে নিত্য খরচের সাথে মিশে না যায়।",
    ]

    assistant = json.dumps({
        "intent": "advice", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_motivation():
    user = random.choice([
        "সেভিংস বাড়াতে চাই, কিন্তু পারছি না",
        "টাকা জমে না, কী করব বলো?",
        "খরচ কন্ট্রোলে আনতে চাই—সাহায্য করবে?",
        "আমার ফাইন্যান্স নিয়ে একটু টেনশন হচ্ছে",
        "টাকা জমছে না ভাই, উপায় দাও",
    ])

    responses = [
        "ছোট ছোট পদক্ষেপ নিন। আজই শুরু করতে পারেন ১০০ টাকা সেভ করে।\n\n"
        "চিন্তা করবেন না — আমরা একসঙ্গে কাজ করব। আগে খরচ কোথায় হচ্ছে দেখি, তারপর কমানোর উপায় বের করব।",
        "টেনশন না। শুরু করুন আজ থেকে:\n"
        "১. প্রতিদিন ৫০ টাকা করে সেভ করুন\n"
        "২. অপ্রয়োজনীয় কেনাকাটা বন্ধ করুন\n"
        "৩. বাজেট বানিয়ে চলুন\n\n"
        "Hisab AI আপনার পাশে আছে। দেখবেন, এক মাসেই পরিবর্তন আসবে।",
        "একসাথে বড় কিছু ভাবার দরকার নেই। ছোট শুরু করলেই হবে।\n\n"
        "আজকের টার্গেট: শুধু আজকের খরচ লিখুন। আগামীকাল দেখব বাঁচানোর উপায়।",
    ]

    assistant = json.dumps({
        "intent": "advice", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_income_tips():
    user = random.choice([
        "ইনকাম বাড়ানোর উপায় বলো",
        "আয় কিভাবে বাড়ানো যায়?",
        "স্যালারি ছাড়া অন্য উপায়ে ইনকাম কীভাবে করব?",
        "ফ্রিল্যান্সিং শুরু করব কীভাবে?",
    ])

    responses = [
        "ইনকাম বাড়ানোর কিছু আইডিয়া:\n"
        "• ফ্রিল্যান্সিং — আপনার স্কিল দেখে কাজ নিতে পারেন\n"
        "• টিউশনি — পড়াতে পারলে ভালো ইনকাম\n"
        "• ছোট ব্যবসা — অনলাইনে কিছু শুরু করতে পারেন\n\n"
        "শুরুতে টাকা না থাকলেও — সময় দিন, ধীরে ধীরে হবে।",
        "আজকের যুগে ইনকামের অনেক অপশন আছে।\n\n"
        "আপনার কী কী স্কিল আছে সেটা দেখুন। তারপর সেটাকে কাজে লাগানোর প্ল্যান করি। আমার সাহায্য লাগলে জানাবেন।",
    ]

    assistant = json.dumps({
        "intent": "advice", "slots": {},
        "action": "reply", "response": random.choice(responses), "missing_fields": [],
        "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Conversation generators ────────────────────────────────────────────────

def gen_natural_greeting():
    ctx = fake_context()
    bal = ctx["balance"]

    user = random.choice([
        "হ্যালো!", "হাই!", "আসসালামু আলাইকুম", "শুরু করা যাক",
        "হ্যালো Hisab AI", "ওহে!",
    ])

    responses = [
        f"ওয়ালাইকুম আসসালাম! আপনার বর্তমান ব্যালেন্স **{bal:,} টাকা**। বলুন কী করবেন?",
        f"হ্যালো! আপনার ব্যালেন্স এখন **{bal:,} টাকা**। নতুন কোনো খরচ বা ইনকাম আছে?",
        f"হাই! আছেন কেমন? ব্যালেন্স আছে **{bal:,} টাকা**। কিছু দরকার হলে জানাবেন।",
    ]

    assistant = json.dumps({
        "intent": "greeting", "slots": {},
        "action": "greeting", "response": random.choice(responses), "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(balance=bal)},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_praise():
    user = random.choice([
        "ধন্যবাদ", "থ্যাংকস!", "ভালো লাগলো", "দারুণ!",
        "চমৎকার!", "ধন্যবাদ তোমাকে", "তুমি দারুণ",
    ])

    responses = [
        "আপনাকেও ধন্যবাদ! আর কী সাহায্য দরকার?",
        "থ্যাংকস! আমি Hisab AI — সবসময় আপনার জন্য। বলুন কী করবেন?",
        "ভালো লাগলো শুনে! আর কী করতে পারি?",
        "ধন্যবাদ! আপনার টাকা-পয়সার হিসাব রাখতেই তো আমি।",
    ]

    assistant = json.dumps({
        "intent": "greeting", "slots": {},
        "action": "greeting", "response": random.choice(responses), "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_natural_goodbye():
    user = random.choice([
        "যাই তাহলে", "bye", "বাই", "আচ্ছা পরে কথা হবে",
        "ঠিক আছে, আসি", "চলি তাহলে",
    ])

    responses = [
        "আচ্ছা, আসি তাহলে। আবার আসবেন যখন খরচ বা ইনকাম জানাতে চান।",
        "বাই! আপনার দিন শুভ হোক। Hisab AI সবসময় প্রস্তুত।",
        "ভালো থাকবেন! আপনার লেনদেন ট্র্যাক করতে তৈরি আছি।",
    ]

    assistant = json.dumps({
        "intent": "greeting", "slots": {},
        "action": "greeting", "response": random.choice(responses), "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── All generators ─────────────────────────────────────────────────────────
GENERATORS = {
    "analysis_top": (gen_natural_top_category, 60),
    "analysis_breakdown": (gen_natural_breakdown, 40),
    "analysis_monthly": (gen_natural_monthly, 60),
    "analysis_compare": (gen_natural_compare, 30),
    "analysis_specific": (gen_natural_specific_cat, 50),
    "advice_save": (gen_natural_save_tips, 60),
    "advice_category": (gen_natural_cat_advice, 40),
    "advice_budget": (gen_natural_budget, 35),
    "advice_emergency": (gen_natural_emergency, 25),
    "advice_motivation": (gen_natural_motivation, 35),
    "advice_income": (gen_natural_income_tips, 25),
    "greeting": (gen_natural_greeting, 25),
    "praise": (gen_natural_praise, 15),
    "goodbye": (gen_natural_goodbye, 15),
}

def main():
    all_examples = []
    for name, (gen_fn, count) in GENERATORS.items():
        # Each generator called 3x with different random outcomes
        # → same question type gets 3 different responses
        for i in range(count):
            for _ in range(3):
                try:
                    all_examples.append(gen_fn())
                except Exception as e:
                    print(f"Error in {name}#{i}: {e}")

    random.shuffle(all_examples)

    path = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw/analysis_advice_3x.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Total: {len(all_examples)}")

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

    print("\n── Samples ──")
    for ex in random.sample(all_examples, min(5, len(all_examples))):
        user_msg = [m for m in ex["messages"] if m["role"] == "user"][0]["content"]
        asst = [m for m in ex["messages"] if m["role"] == "assistant"][0]["content"]
        try:
            parsed = json.loads(asst)
            print(f'  U: {user_msg}')
            print(f'  AI: {parsed.get("response", "")[:150]}')
            print()
        except:
            pass

if __name__ == "__main__":
    main()
