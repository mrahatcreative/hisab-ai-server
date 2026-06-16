"""
Hisab Pata — Multi-Turn Note Detail Gathering Generator
Generates examples where user gives thin note → AI asks → user adds detail

Pattern-based: model learns that ANY combination of
(reason/context) + (location) + (what) + (purpose_word) = thick note
NOT just "reason + location + item + বাবদ খরচ" template
"""

import json, random

random.seed(42)

CATEGORIES = {
    "Transport": ["রিক্সা ভাড়া", "বাস ভাড়া", "উবার ভাড়া", "সিএনজি ভাড়া", "পেট্রোল খরচ", "ট্রেন ভাড়া", "লঞ্চের টিকিট", "ট্যাক্সি ভাড়া", "বাইক পেট্রোল", "পার্কিং খরচ"],
    "Mobile Recharge": ["মোবাইল রিচার্জ", "ফোন রিচার্জ", "ডেটা প্যাকেজ", "ফোন ব্যালেন্স", "ইন্টারনেট প্যাকেজ", "বাংলালিংক রিচার্জ", "রিচার্জ কার্ড"],
    "Postage": ["কুরিয়ার খরচ", "পার্সেল খরচ", "ডাক খরচ", "চিঠি পাঠানো", "নথি কুরিয়ার", "পোস্ট অফিস খরচ"],
    "Publication": ["বই কেনা", "ম্যাগাজিন কেনা", "পাঠ্যবই", "উপন্যাস", "পত্রিকা কেনা", "স্কুলের বই"],
    "Office Stationery": ["কলম কেনা", "খাতা কেনা", "স্টেশনারি", "ফাইল কেনা", "নোটপ্যাড", "কাগজ কেনা"],
    "Tips": ["টিপস দেওয়া", "বখশিশ দেওয়া", "ডেলিভারি বয় টিপস", "ওয়েটার টিপস"],
    "Donation": ["দান করা", "সদকা দেওয়া", "জাকাত দেওয়া", "মসজিদে দান", "এতিমখানায় দান", "গরিবকে সাহায্য"],
    "Others": ["লাঞ্চ", "ডিনার", "বাজার", "ওষুধ কেনা", "কাপড় কেনা", "মেডিসিন", "হেয়ারকাট", "সিনেমা দেখা", "বিউটি পার্লার", "ডাক্তারের ফি"],
}

REASONS = [
    "অফিসের কাজে", "জরুরী কাজে", "ব্যক্তিগত প্রয়োজনে", "পরিবারের জন্য",
    "অসুস্থ বলে", "স্কুলের কাজে", "বাজার করতে", "আত্মীয়ের বাড়িতে",
    "দাওয়াত খেতে", "হাঁটতে গিয়ে", "ঘুরতে গিয়ে", "বন্ধুর জন্য",
    "রাতে দরকার ছিল", "সকালে বের হয়ে", "অফিস ফেরার পথে",
]
LOCATIONS = [
    "পল্টন থেকে মগবাজারে", "বাড্ডা থেকে গুলশানে", "ধানমন্ডি থেকে কলাবাগানে",
    "মিরপুর থেকে গুলিস্তানে", "মোহাম্মদপুর থেকে নিউমার্কেটে",
    "এলিফ্যান্ট রোড থেকে শাহবাগে", "উত্তরা থেকে মতিঝিলে",
    "মালিবাগ থেকে রামপুরায়", "বসুন্ধরা থেকে মিরপুরে",
    "বারিধারা থেকে ফার্মগেটে", "বনানী থেকে আগারগাঁওয়ে",
    "শান্তিনগর থেকে মগবাজারে", "কাজীপাড়া থেকে শেওড়াপাড়ায়",
    "নিউমার্কেটে", "বসুন্ধরা শপিং কমপ্লেক্সে", "জামুনা ফিউচার পার্কে",
    "বাসায়", "অফিসে", "বাজারে", "হাসপাতালে", "ডাক্তারের চেম্বারে",
    "স্কুলে", "মসজিদে", "বইয়ের দোকানে", "ফার্মেসিতে", "রেস্টুরেন্টে",
]
AMOUNTS = [50, 100, 150, 200, 300, 500, 1000, 1500, 2000, 3000, 5000]

def system_prompt(categories=None):
    cats = categories or list(CATEGORIES.keys())
    return f"book_type: personal\ncategories: {', '.join(cats)}\nbalance: 12500"

def note_has_detail(note):
    elements = 0
    if any(kw in note for kw in ["ভাড়া", "খরচ", "লাঞ্চ", "বাজার", "দান", "টিপস", "রিচার্জ", "কেনা", "পাঠানো"]):
        elements += 1
    if any(kw in note for kw in ["জন্য", "কারণ", "কাজে", "বাবদ", "হেতু", "পথে", "সময়", "লাগলো"]):
        elements += 1
    if any(kw in note for kw in ["থেকে", "যায়", "গিয়ে", "এসে", "হয়ে", "ফিরে"]):
        elements += 1
    if len(note) > 30:
        elements += 1
    return elements >= 3

def make_thick_note_varied(reason, loc, expense_item):
    patterns = [
        lambda: f"{reason} {loc} {expense_item} বাবদ খরচ",
        lambda: f"{expense_item} {loc} {reason}",
        lambda: f"{reason} {loc} যাওয়ার পথে {expense_item}",
        lambda: f"{loc} থেকে ফেরার সময় {reason} {expense_item}",
        lambda: f"{loc} {reason} {expense_item} লাগলো",
        lambda: f"{loc} {expense_item} খরচ {reason}",
    ]
    return random.choice(patterns)()

def gen_2turn_thin_to_thick():
    cat = random.choice(list(CATEGORIES.keys()))
    amount = random.choice(AMOUNTS)
    expense = random.choice(CATEGORIES[cat])

    user_t1 = random.choice([
        f"{amount} টাকা {expense} খরচ করেছি",
        f"আজ {amount} টাকা {expense} দিয়েছি",
        f"{amount} taka {expense} khorch",
        f"{amount} টাকা {expense}",
    ])

    asst_t1 = json.dumps({
        "intent": "expense", "slots": {"amount": amount},
        "action": "ask", "missing_fields": ["note_detail"],
        "question": random.choice([
            "কীভাবে, কেন, কোথায় এই খরচ করছেন? বিস্তারিত জানান।",
            "বিস্তারিত কী? কোথায় আর কেন খরচ করলেন?",
            "কারণ এবং লোকেশন জানালে নোট রাখতে সুবিধা হয়। বিস্তারিত বলুন।",
        ]),
        "confidence": round(random.uniform(0.7, 0.85), 2)
    }, ensure_ascii=False)

    reason = random.choice(REASONS)
    loc = random.choice(LOCATIONS)
    thick_note = make_thick_note_varied(reason, loc, expense)

    user_t2 = random.choice([
        f"{reason} {loc} গিয়েছিলাম",
        f"{loc} {reason} যাওয়ার জন্য",
        f"{reason} {loc}",
        f"{thick_note}",
    ])

    asst_t2 = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.88, 0.96), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_t1},
        {"role": "assistant", "content": asst_t1},
        {"role": "user", "content": user_t2},
        {"role": "assistant", "content": asst_t2}
    ]}

def gen_3turn_progressive():
    cat = random.choice(list(CATEGORIES.keys()))
    amount = random.choice(AMOUNTS)
    expense = random.choice(CATEGORIES[cat])

    user_t1 = random.choice([
        f"{amount} টাকা খরচ করেছি",
        f"আজ {amount} টাকা খরচ",
        f"{amount} taka khorch",
    ])
    asst_t1 = json.dumps({
        "intent": "expense", "slots": {"amount": amount},
        "action": "ask", "missing_fields": ["category", "note_detail"],
        "question": random.choice([
            "কিসের জন্য খরচ করছেন? বিস্তারিত জানান।",
            "কেন খরচ? আর কীসের জন্য? বিস্তারিত বলুন।",
        ]),
        "confidence": round(random.uniform(0.6, 0.8), 2)
    }, ensure_ascii=False)

    user_t2 = random.choice([
        f"{expense}",
        f"{expense} খরচ",
        f"{expense} khorch",
    ])
    asst_t2 = json.dumps({
        "intent": "expense", "slots": {"amount": amount},
        "action": "ask", "missing_fields": ["note_detail"],
        "question": random.choice([
            "কেন এবং কোথায় এই খরচ করছেন? বিস্তারিত জানান।",
            "কারণ আর লোকেশন জানান। যাতে নোট বিস্তারিত হয়।",
        ]),
        "confidence": round(random.uniform(0.7, 0.85), 2)
    }, ensure_ascii=False)

    reason = random.choice(REASONS)
    loc = random.choice(LOCATIONS)
    thick_note = make_thick_note_varied(reason, loc, expense)

    user_t3 = random.choice([
        f"{reason} {loc} গিয়েছিলাম",
        f"{loc} {reason}",
        f"{reason} {loc} যাওয়ার জন্য",
    ])
    asst_t3 = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.88, 0.96), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_t1},
        {"role": "assistant", "content": asst_t1},
        {"role": "user", "content": user_t2},
        {"role": "assistant", "content": asst_t2},
        {"role": "user", "content": user_t3},
        {"role": "assistant", "content": asst_t3}
    ]}

def gen_user_resists_detail():
    cat = random.choice(list(CATEGORIES.keys()))
    amount = random.choice(AMOUNTS)
    expense = random.choice(CATEGORIES[cat])
    user_t1 = random.choice([
        f"{amount} টাকা {expense} খরচ করেছি",
        f"{amount} taka {expense} khorch",
    ])

    asst_t1 = json.dumps({
        "intent": "expense", "slots": {"amount": amount},
        "action": "ask", "missing_fields": ["note_detail"],
        "question": random.choice([
            "বিস্তারিত জানান। কোথায়, কেন এই খরচ করছেন?",
            "ডিটেল দিলে নোট ভালো হয়। কোথায় আর কেন ব্যয় করলেন?",
        ]),
        "confidence": round(random.uniform(0.7, 0.85), 2)
    }, ensure_ascii=False)

    user_t2 = random.choice([
        "শুধু খরচ, বেশি কিছু না",
        "খালি খরচ করছি, কিছু বলার নাই",
        "just খরচ, detail দরকার নাই",
        "detail দিতে চাই না",
        "শুধু নোট রাখো",
    ])
    asst_t2 = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": expense},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.5, 0.65), 2),
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_t1},
        {"role": "assistant", "content": asst_t1},
        {"role": "user", "content": user_t2},
        {"role": "assistant", "content": asst_t2}
    ]}

def gen_correction_flow():
    cat = random.choice(list(CATEGORIES.keys()))
    amount = random.choice(AMOUNTS)
    expense = random.choice(CATEGORIES[cat])
    new_amount = amount + random.choice([50, 100])

    user_t1 = random.choice([
        f"{amount} টাকা {expense} খরচ করেছি",
        f"{amount} taka {expense} diyechi",
    ])
    thin_note = expense
    asst_t1 = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "note": thin_note},
        "action": "ask", "missing_fields": ["note_detail"],
        "question": "বিস্তারিত জানান।",
        "confidence": 0.78
    }, ensure_ascii=False)

    user_t2 = random.choice([
        f"ওইটা না, {new_amount} টাকা ছিল",
        f"না না, {new_amount} taka hobe",
        f"arre {new_amount} টাকা বলেছিলাম",
    ])
    asst_t2 = json.dumps({
        "intent": "edit", "slots": {"amount": new_amount},
        "action": "confirm", "missing_fields": [], "confidence": 0.85
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_t1},
        {"role": "assistant", "content": asst_t1},
        {"role": "user", "content": user_t2},
        {"role": "assistant", "content": asst_t2}
    ]}

GENERATORS = [
    (gen_2turn_thin_to_thick, 300),
    (gen_3turn_progressive, 100),
    (gen_user_resists_detail, 50),
    (gen_correction_flow, 50),
]

def main():
    all_examples = []
    for gen_fn, count in GENERATORS:
        for i in range(count):
            all_examples.append(gen_fn())
    random.shuffle(all_examples)
    print(f"Multi-turn generated: {len(all_examples)}")

    path = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw/multi_turn.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Saved to: {path}")

if __name__ == "__main__":
    main()
