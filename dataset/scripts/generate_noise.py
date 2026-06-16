"""
Hisab Pata — Noise & Banglish Pattern Dataset Generator
Teaches Qwen 1.5B to handle Bengali spelling mistakes + Banglish.

Key insight: Instead of memorizing "correct → wrong" pairs,
model learns PHONETIC patterns:
  - Vowel dropping: টাকা → টকা, কিনেছি → কিনছি
  - Consonant softening: করেছি → করসি, দিয়েছি → দিছি
  - Banglish transliteration: khoroch, taka, diyechi
  - Keyboard typos (adjacent key errors)
  - Homophones: স / শ / ষ confusion
  - Short forms: bazar → bajar, kore → kore
"""

import json, random

random.seed(777)

AVAILABLE_CATEGORIES = [
    "Transport", "Mobile Recharge", "Postage", "Publication",
    "Office Stationery", "Tips", "Donation", "Others", "Salary"
]

AMOUNTS = [50, 100, 120, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800,
           1000, 1200, 1500, 2000, 2500, 3000, 5000, 8000, 10000]

BENGALI_VOWEL_DROP = {
    "টাকা": ["টকা", "টাকা"], "কিনেছি": ["কিনছি", "কিনসি"],
    "দিয়েছি": ["দিছি", "দিসি"], "করেছি": ["করছি", "করসি", "করি"],
    "গিয়েছি": ["গেছি", "গেসি"], "বলেছেন": ["বলসেন"],
    "হয়েছে": ["হয়ছে", "হয়সে"], "পারবেন": ["পারবেন", "পারবো"],
    "বলবেন": ["বলবেন"], "জানান": ["জানান", "জানান"],
}

BENGALI_CONSONANT_SOFTEN = {
    "খরচ": ["খচর", "খরিচ", "খরছ"], "জন্য": ["জন্ন", "জোনো"],
    "বাবদ": ["বাদ", "বাবুদ"], "থেকে": ["থেক", "থিকা", "থেকে"],
    "কাজে": ["কাজে", "কাজা"], "বাজার": ["বাজার", "বাজারে"],
    "ওষুধ": ["ওষুধ", "ওসুধ", "ওষুদ"], "কেনা": ["কেনা", "কিনা"],
    "পাঠানো": ["পাঠানো", "পাঠান"], "দোকান": ["দোকান", "ডোকান"],
    "মাসিক": ["মাসিক", "মাসেক"], "পেয়েছি": ["পেয়েছি", "পাইছি"],
    "এসেছে": ["এসেছে", "আইছে"], "জন": ["জন", "জোন"],
}

BENGALI_HOMOPHONES = {
    "শ": "স", "স": "শ", "ষ": "স", "শ": "ষ",
    "ণ": "ন", "ন": "ণ", "ৎ": "ত",
}

REASONS = [
    "অফিসের কাজে", "জরুরী কাজে", "ব্যক্তিগত প্রয়োজনে", "পরিবারের জন্য",
    "অসুস্থ বলে", "স্কুলের কাজে", "বাজার করতে", "আত্মীয়ের বাড়িতে",
]

LOCATIONS = [
    "পল্টন", "বাড্ডা", "গুলশান", "ধানমন্ডি", "মিরপুর",
    "উত্তরা", "মোহাম্মদপুর", "নিউমার্কেট", "বসুন্ধরা",
    "হাসপাতালে", "বাসায়", "অফিসে", "ফার্মেসিতে",
]

CATEGORY_EXPENSES = {
    "Transport": ["রিক্সা ভাড়া", "বাস ভাড়া", "উবার ভাড়া", "সিএনজি ভাড়া", "পেট্রোল", "ট্যাক্সি"],
    "Mobile Recharge": ["মোবাইল রিচার্জ", "ফোন রিচার্জ", "ডেটা প্যাকেজ"],
    "Postage": ["কুরিয়ার খরচ", "পার্সেল খরচ", "ডাক খরচ"],
    "Publication": ["বই কেনা", "ম্যাগাজিন", "পাঠ্যবই"],
    "Office Stationery": ["কলম", "খাতা", "স্টেশনারি", "ফাইল"],
    "Tips": ["টিপস", "বখশিশ"],
    "Donation": ["দান", "সদকা", "জাকাত"],
    "Others": ["লাঞ্চ", "ডিনার", "বাজার", "ওষুধ", "কাপড়"],
}

BANGLISH_VOCAB = {
    "taka": ["taka", "taka", "tk"], "khorch": ["khorch", "khoroch", "khoros"],
    "diyechi": ["diyechi", "dichi", "disi", "deichi"],
    "korsi": ["korsi", "korchi", "kortesi"], "laglo": ["laglo", "lagse", "lagche"],
    "theke": ["theke", "theka", "theke"], "jonno": ["jonno", "jono", "jon"],
    "babod": ["babod", "babad", "babude"],
    "kinechi": ["kinechi", "kinchi", "kinesi"],
    "pathaisi": ["pathaisi", "pathaichi", "pathachi"],
    "ace": ["ace", "ache", "ase"],
}

CONTACTS = ["Rahim", "Karim", "Suman", "Nasrin", "Fatema", "Jamal", "Sajid", "Tania", "Rahat", "Shaon"]

def system_prompt():
    return f"book_type: personal\ncategories: {', '.join(AVAILABLE_CATEGORIES)}\nbalance: 12500"

def apply_banglish_bengali_mix(note):
    """Convert Bengali note to mixed Banglish/Bengali."""
    taka_variants = random.choice(["taka", "taka", "tk", "টাকা"])
    khorch_variants = random.choice(["khorch", "khoroch", "khoros", "khorcha"])
    
    result = note
    replacements = {
        "টাকা": taka_variants,
        "খরচ": khorch_variants,
        "জন্য": random.choice(["jonno", "jono", "jon"]),
        "বাবদ": random.choice(["babod", "babad"]),
        "থেকে": random.choice(["theke", "theka"]),
        "দেওয়া": random.choice(["deowa", "deoa"]),
        "দিয়েছি": random.choice(["diyechi", "dichi"]),
        "করেছি": random.choice(["korsi", "korchi", "korechi"]),
        "বলেছেন": "bolechen",
        "বাজার": random.choice(["bazar", "bajar"]),
        "কুরিয়ার": random.choice(["courier", "kurier"]),
        "রিচার্জ": random.choice(["recharge", "richarge"]),
        "ডিনার": random.choice(["dinner", "dinar"]),
        "লাঞ্চ": random.choice(["lunch", "lanch"]),
        "হাসপাতালে": "hospital e",
        "অফিসে": "office e",
        "বাসায়": "basa ye",
    }
    for bengali, banglish in replacements.items():
        if bengali in result and random.random() > 0.4:
            result = result.replace(bengali, banglish, 1)
    return result

def apply_bengali_spelling_mistakes(note):
    """Apply realistic Bengali spelling errors."""
    result = note
    
    # Vowel drops
    for correct, wrongs in BENGALI_VOWEL_DROP.items():
        if correct in result and random.random() > 0.55:
            result = result.replace(correct, random.choice(wrongs), 1)
    
    # Consonant softenings
    for correct, wrongs in BENGALI_CONSONANT_SOFTEN.items():
        if correct in result and random.random() > 0.55:
            result = result.replace(correct, random.choice(wrongs), 1)
    
    # Homophone swaps (10-20% chance per character)
    chars = list(result)
    for i in range(len(chars)):
        for wrong, correct in BENGALI_HOMOPHONES.items():
            if chars[i] == wrong and random.random() > 0.85:
                chars[i] = correct
                break
        for correct, wrong in BENGALI_HOMOPHONES.items():
            if chars[i] == correct and random.random() > 0.88:
                chars[i] = wrong
                break
    
    result = "".join(chars)
    return result

def apply_typo_keyboard(note):
    """Simulate adjacent-key typing errors on Bengali keyboard."""
    # Bengali vowel adjacency: অ আ ই ঈ উ ঊ এ ঐ ও ঔ
    adjacent_vowels = {"আ": "অ", "ই": "ঈ", "উ": "ঊ", "এ": "অ", "ও": "আ"}
    # Bengali consonant adjacency
    adjacent_consonants = {"ক": "গ", "গ": "ক", "চ": "ছ", "জ": "ঝ", "ট": "ঠ", "ড": "ঢ", "ত": "থ", "দ": "ধ", "প": "ফ", "ব": "ভ"}
    
    result = note
    if random.random() > 0.7:
        # Swap one random consonant
        for correct, wrong in adjacent_consonants.items():
            if correct in result and random.random() > 0.85:
                result = result.replace(correct, wrong, 1)
                break
    if random.random() > 0.7:
        # Swap one random vowel
        for correct, wrong in adjacent_vowels.items():
            if correct in result and random.random() > 0.85:
                result = result.replace(correct, wrong, 1)
                break
    return result

def generate_thick_note():
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    expense_item = random.choice(CATEGORY_EXPENSES[cat])
    reason = random.choice(REASONS)
    loc = random.choice(LOCATIONS)
    patterns = [
        lambda: f"{reason} {loc} {expense_item} বাবদ খরচ",
        lambda: f"{expense_item} {loc} {reason} জন্যদেওয়া",
        lambda: f"{loc} {reason} {expense_item} লাগলো",
        lambda: f"{reason} {loc} যাওয়ার পথে {expense_item}",
    ]
    return cat, random.choice(patterns)()

# ── Generator: Banglish only ────────────────────────────────────────────
def gen_banglish_expense():
    amount = random.choice(AMOUNTS)
    cat, thick_note = generate_thick_note()
    banglish_note = apply_banglish_bengali_mix(thick_note)
    
    user = random.choice([
        f"ajke {amount} taka {banglish_note}",
        f"kal {amount} taka {banglish_note} khorch korsi",
        f"{amount} taka {banglish_note}",
        f"today {amount} taka {banglish_note}",
        f"aj {amount} tk {banglish_note}",
    ])
    
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.65, 0.82), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_banglish_income():
    amount = random.choice([5000, 8000, 10000, 15000, 20000, 30000])
    user = random.choice([
        f"salary paichi {amount} taka",
        f"{amount} taka income hoyeche salary babod",
        f"bheton paisi {amount} taka",
        f"maine esheche {amount} taka",
    ])
    assistant = json.dumps({
        "intent": "income", "slots": {"amount": amount, "category": "Salary", "note": "বেতন বাবদ ইনকাম"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_banglish_send():
    amount = random.choice([200, 500, 1000, 2000])
    contact = random.choice(CONTACTS)
    user = random.choice([
        f"{contact} ke {amount} send korsi",
        f"{contact} k {amount} taka pathaisi",
        f"{contact} er kase {amount} taka send",
        f"send korsi {amount} taka {contact} ke",
    ])
    assistant = json.dumps({
        "intent": "send", "slots": {"amount": amount, "category": "Send", "contact": contact, "note": f"{contact} কে সেন্ড"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.82, 0.95), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Generator: Bengali spelling mistakes ─────────────────────────────────
def gen_spelling_expense():
    amount = random.choice(AMOUNTS)
    cat, thick_note = generate_thick_note()
    corrupted_note = apply_bengali_spelling_mistakes(thick_note)
    corrupted_note = apply_typo_keyboard(corrupted_note)
    
    user = random.choice([
        f"আজ {amount} টাকা {corrupted_note}",
        f"গতকাল {amount} টাকা {corrupted_note} করেছি",
        f"{amount} টাকা {corrupted_note} দিয়েছি",
        f"আজকে {amount} টাকা {corrupted_note} খরচ",
    ])
    
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.65, 0.82), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_spelling_query():
    queries = {
        "balance": [
            "ব্যালেন্স কত?", "কত টকা আছে?", "ব্যালেনস কতো?",
            "কত বাকি?", "মোর বেলেন্স দেখাও",
            "আমার বেলেন্স কতো?",
        ],
        "summary": [
            "এই মাসে কত খচর করসি?", "সামারি দেখাও",
            "এই মাশে কত খরচ আর কত ইনকাম?",
            "গত মাসে কত খরচ?",
        ],
        "list": [
            "লিস্ট দাও", "আজকের ট্রানজেকসন দেখাও",
            "গত ৭ দিনের তালিকা দাও",
        ],
    }
    intent = random.choice(list(queries.keys()))
    user = random.choice(queries[intent])
    assistant = json.dumps({
        "intent": intent, "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.85, 0.98), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Generator: heavy mixed (both Banglish + spelling errors) ─────────────
def gen_heavy_noise_expense():
    amount = random.choice(AMOUNTS)
    cat, thick_note = generate_thick_note()
    
    # First apply Banglish, then Bengali spelling mistakes on top
    noisy = apply_banglish_bengali_mix(thick_note)
    noisy = apply_bengali_spelling_mistakes(noisy)
    noisy = apply_typo_keyboard(noisy)
    
    # Mix English structure too
    prefixes = [f"ajke", f"kal", f"today", f"aj", ""]
    suffixes = [f"khorch korsi", f"diyechi", f"khortesi", f"lagse", ""]
    
    user = f"{random.choice(prefixes)} {amount} {'tk' if random.random()>0.5 else 'taka'} {noisy} {random.choice(suffixes)}".strip()
    
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.5, 0.72), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_heavy_noise_send():
    amount = random.choice([200, 500, 1000])
    contact = random.choice(CONTACTS)
    user = random.choice([
        f"{contact} k {amount} tk send disi",
        f"{contact} ke {amount} taka pathaichi",
        f"send korechi {amount} taka {contact} er kase",
        f"{contact} er jnno {amount} taka pathaice",
    ])
    assistant = json.dumps({
        "intent": "send", "slots": {"amount": amount, "category": "Send", "contact": contact, "note": f"{contact} কে সেন্ড"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.70, 0.88), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_heavy_noise_income():
    amount = random.choice([5000, 10000, 15000, 25000])
    user = random.choice([
        f"bheton ace {amount} tk",
        f"selary paisi {amount} taka",
        f"income {amount} tk sallary theke",
        f"maine esheche {amount} tk",
    ])
    assistant = json.dumps({
        "intent": "income", "slots": {"amount": amount, "category": "Salary", "note": "বেতন বাবদ ইনকাম"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.75, 0.88), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

GENERATORS = {
    "banglish_expense": (gen_banglish_expense, 200),
    "banglish_income": (gen_banglish_income, 50),
    "banglish_send": (gen_banglish_send, 50),
    "spelling_expense": (gen_spelling_expense, 200),
    "spelling_query": (gen_spelling_query, 100),
    "heavy_noise_expense": (gen_heavy_noise_expense, 200),
    "heavy_noise_send": (gen_heavy_noise_send, 50),
    "heavy_noise_income": (gen_heavy_noise_income, 50),
}

def main():
    all_examples = []
    for name, (gen_fn, count) in GENERATORS.items():
        for i in range(count):
            try:
                all_examples.append(gen_fn())
            except Exception as e:
                print(f"Error in {name}#{i}: {e}")

    random.shuffle(all_examples)
    
    path = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw/noise_banglish.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    
    print(f"Total noise/Banglish examples: {len(all_examples)}")
    
    # Show samples
    print("\n── Samples ──")
    for ex in random.sample(all_examples, min(5, len(all_examples))):
        user_msg = [m for m in ex["messages"] if m["role"] == "user"][0]["content"]
        asst_msg = [m for m in ex["messages"] if m["role"] == "assistant"][0]["content"]
        print(f"  USER: {user_msg}")
        print(f"  AI:   {asst_msg[:100]}")
        print()

if __name__ == "__main__":
    main()
