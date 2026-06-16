"""
Hisab Pata — Template-Based Dataset Generator (Phase 1)
Generates ~1,500 training examples in ChatML format for Qwen 1.5B fine-tuning.

Output: dataset/raw/template_based.jsonl
Format: {"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
"""

import json, random, itertools
from datetime import datetime, timedelta

random.seed(42)

# ── Configuration ──────────────────────────────────────────────────────────

AVAILABLE_CATEGORIES = [
    "Transport", "Mobile Recharge", "Postage", "Publication",
    "Office Stationery", "Tips", "Donation", "Others", "Salary"
]
BALANCE_OPTIONS = [0, 500, 1200, 3500, 8500, 12500, 50000, 125000]
AMOUNTS = [50, 100, 120, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800, 1000, 1200, 1500, 2000, 2500, 3000, 5000, 8000, 10000, 15000, 20000, 30000, 50000]
DATES = ["আজ", "গতকাল", "পরশু", "১৫ জুন", "১০ জুন ২০২৫", "গত সপ্তাহে", "এই সপ্তাহে"]

# ── Bengali numbers for textual variants ────────────────────────────────────
BENGALI_NUMBERS = {
    50: "পঞ্চাশ", 100: "একশ", 200: "দুইশ", 300: "তিনশ", 500: "পাঁচশ",
    1000: "এক হাজার", 2000: "দুই হাজার", 5000: "পাঁচ হাজার", 10000: "দশ হাজার"
}

CONTACTS = ["রহিম", "করিম", "সুমন", "নাসরিন", "ফাতেমা", "জামাল", "সাজিদ", "তানিয়া", "রাহাত", "শাওন", "সাকিব", "নাঈম", "রাশেদ"]
NOTES = ["লাঞ্চ", "ডিনার", "বাজার", "ওষুধ", "বই", "কাপড়", "ইলেকট্রিসিটি বিল", "ইন্টারনেট বিল", "পানি বিল"]
BENGALI_CATEGORIES = {
    "Transport": "পরিবহন", "Mobile Recharge": "মোবাইল রিচার্জ", "Postage": "ডাক খরচ",
    "Publication": "প্রকাশনা", "Office Stationery": "অফিস স্টেশনারি",
    "Tips": "টিপস", "Donation": "দান", "Others": "অন্যান্য", "Salary": "বেতন"
}
BANGLISH_CATEGORIES = {
    "Transport": "transport", "Mobile Recharge": "mobile recharge", "Postage": "postage",
    "Publication": "publication", "Office Stationery": "stationery",
    "Tips": "tips", "Donation": "donation", "Others": "others", "Salary": "salary"
}

# ── Expanded expense items (many per category, pattern-based) ───────────────
# The model should learn: words about movement/vehicle → Transport
#                          words about phone/internet → Mobile Recharge
#                          words about mail/parcel → Postage
#                          etc.
CATEGORY_EXPENSES = {
    "Transport": [
        "রিক্সা ভাড়া", "বাস ভাড়া", "উবার ভাড়া", "পেট্রোল খরচ", "নৌকা ভাড়া",
        "সিএনজি ভাড়া", "লোকাল বাস খরচ", "ট্রেন ভাড়া", "লঞ্চের টিকিট",
        "গাড়ির তেল", "পানিতে নৌকা দিয়ে যাওয়া", "রাস্তা পারাপার ভাড়া",
        "ব্রিজ টোল", "পার্কিং খরচ", "ট্যাক্সি ভাড়া", "অটোরিক্সা ভাড়া",
        "লিফট দেওয়া", "বাইক পেট্রোল", "মাইক্রোবাস খরচ",
    ],
    "Mobile Recharge": [
        "মোবাইল রিচার্জ", "ফোন রিচার্জ", "ডেটা প্যাকেজ রিচার্জ",
        "সিম রিচার্জ", "ফোন ব্যালেন্স", "ইন্টারনেট প্যাকেজ",
        "মোবাইল ডেটা", "জিপি রিচার্জ", "বাংলালিংক রিচার্জ",
        "এয়ারটেল রিচার্জ", "রবি রিচার্জ", "ফোনের টাকা উঠানো",
        "স্ক্র্যাচ কার্ড কেনা", "রিচার্জ কার্ড",
    ],
    "Postage": [
        "কুরিয়ার খরচ", "ডাক খরচ", "পার্সেল পাঠানোর খরচ",
        "চিঠি পাঠানো", "নথি পাঠানোর কুরিয়ার", "ডাক টিকিট",
        "পোস্ট অফিস খরচ", "রেজিস্ট্রি ডাক", "এসএমএস ব্যালেন্স",
        "বন্দর খরচ পার্সেলের",
    ],
    "Publication": [
        "পাঠ্যবই", "উপন্যাস", "ম্যাগাজিন", "প্রকাশনা খরচ",
        "বই কেনা", "গল্পের বই", "আর্টিকেল প্রিন্ট",
        "পেপারব্যাক বই", "ই-বুক কিনলাম", "পত্রিকা কেনা",
        "সাপ্তাহিক ম্যাগাজিন", "স্কুলের পাঠ্যবই",
    ],
    "Office Stationery": [
        "কলম", "খাতা", "ফাইল", "পেন", "কাগজ",
        "পেনসিল", "ইরেজার", "টেপ", "গ্লু", "স্ট্যাপলার",
        "কাগজ ক্লিপ", "ফোল্ডার", "নোটপ্যাড", "ডায়েরি",
        "হোয়াইটবোর্ড মার্কার", "শীট কাগজ", "খাম",
        "ক্যালকুলেটর", "সাদা কাগজ", "পিন",
    ],
    "Tips": [
        "রেস্টুরেন্ট টিপস", "হোটেল বয় টিপস", "ডেলিভারি বয় টিপস",
        "বয় টিপস", "টিপস দিলাম", "ওয়েটার টিপস",
        "বারান্দা দারোয়ান টিপস", "বিল গোল দিলাম", "পার্কিং বয় টিপস",
    ],
    "Donation": [
        "মসজিদে দান", "এতিমখানায় দান", "সদকা", "জাকাত", "দান খয়রাত",
        "ফিতরা", "মাদ্রাসায় দান", "গরিবকে দান", "অসহায়কে সাহায্য",
        "মন্দিরে দান", "এতিমকে টাকা", "স্কুল ফান্ডে দান",
        "দুঃস্থকে খাবার দিলাম", "রাস্তার লোককে সাহায্য",
    ],
    "Others": [
        "লাঞ্চ", "ডিনার", "বাজার", "ওষুধ", "কাপড় কেনাকাটা", "সাজসজ্জা",
        "মেডিসিন", "ডাক্তারের ফি", "হাসপাতাল বিল", "বিউটি পার্লার",
        "জিম ফি", "হেয়ারকাট", "নেলসalon", "থিয়েটারের টিকিট",
        "সিনেমা দেখা", "ঘুরতে যাওয়া", "পিকনিক খরচ", "জন্মদিনের পার্টি",
        "বিয়ে উপহার", "ঈদ শপিং", "ল্যাব টেস্ট", "ব্লাড টেস্ট",
        "হোটেলে খাওয়া", "কফি শপ", "রেস্টুরেন্ট এ খাওয়া",
    ],
    "Salary": [
        "মাসিক বেতন", "বেতন", "সেলারি", "বেতন প্রাপ্তি",
        "মাইনে পেয়েছি", "মাস শেষে বেতন", "সেলারি পেয়েছি",
    ],
}

REASONS = [
    "অফিসের কাজে", "জরুরী কাজে", "ব্যক্তিগত প্রয়োজনে", "পরিবারের জন্য",
    "অসুস্থ বলে", "স্কুলের কাজে", "বাজার করতে", "আত্মীয়ের বাড়িতে",
    "দাওয়াত খেতে", "হাঁটতে গিয়ে", "ঘুরতে গিয়ে",
    "বন্ধুর জন্য", "মাকে দিয়ে দিলাম", "ছেলের জন্য",
    "রাতে দরকার ছিল", "সকালে বের হয়ে", "অফিস ফেরার পথে",
    "বাজার থেকে ফিরে", "ছুটির দিনে", "অতিথি এলে",
]

# ── Expanded locations (real Dhaka/Bangladesh places) ──────────────────────
LOCATIONS = [
    # Movement from X to Y
    "পল্টন থেকে মগবাজারে", "বাড্ডা থেকে গুলশানে", "ধানমন্ডি থেকে কলাবাগানে",
    "মিরপুর থেকে গুলিস্তানে", "মোহাম্মদপুর থেকে নিউমার্কেটে",
    "এলিফ্যান্ট রোড থেকে শাহবাগে", "উত্তরা থেকে মতিঝিলে",
    "মালিবাগ থেকে রামপুরায়", "নাখালপাড়া থেকে শ্যামলীতে",
    "বসুন্ধরা থেকে মিরপুরে", "বারিধারা থেকে ফার্মগেটে",
    "বনানী থেকে আগারগাঁওয়ে", "কাকরাইল থেকে পল্টনে",
    "শান্তিনগর থেকে মগবাজারে", "টিকাটুলি থেকে নিউমার্কেটে",
    "কাজীপাড়া থেকে শেওড়াপাড়ায়", "সোহরাওয়ার্দী উদ্যান থেকে শাহবাগে",
    "ঈশ্বরখানি থেকে উত্তরা", "বিমানবন্দর থেকে ফার্মগেট",
    "লালবাগ থেকে গেন্ডারিয়ায়",

    # Shops / Markets / specific locations
    "নিউমার্কেটে", "গাউসুল আজম মার্কেটে", "চাঁদ ম্যারিয়েটে",
    "বসুন্ধরা শপিং কমপ্লেক্সে", "জামুনা ফিউচার পার্কে", "শিমুল স্কয়ারে",
    "রংধনু শপিং সেন্টারে", "কাঁঠাল বাগানের দোকানে",
    "মিরপুর ১ নম্বর গেটে", "মিরপুর ১০ নম্বরে", "গুলশান ১ নম্বরে",
    "গুলশান ২ নম্বরে", "বনানী জামে মসজিদের সামনে",
    "ধানমন্ডি ২৭ নম্বরে", "নাখালপাড়া বাস স্ট্যান্ডে",

    # Generic location phrases
    "বাসায়", "অফিসে", "বাজারে", "হাসপাতালে", "ডাক্তারের চেম্বারে",
    "ল্যাবে", "স্কুলে", "কলেজে", "মাদ্রাসায়", "মসজিদে",
    "বইয়ের দোকানে", "ফার্মেসিতে", "কাপড়ের দোকানে",
    "রেস্টুরেন্টে", "হোটেলে", "পার্কে", "কমিউনিটি সেন্টারে",
]

LOCATION_VERBS_MAP = {
    "আমি": ["যাতায়াত করেছি", "গিয়েছি", "এসেছি", "আসছি"],
    "যাওয়া": ["গেলাম", "যাই", "আসি"],
}

# ── System prompt with AI identity ──────────────────────────────────────────
def system_prompt(book_type="personal", categories=None, balance=12500):
    cat_str = ", ".join(categories or AVAILABLE_CATEGORIES)
    return f"book_type: {book_type}\ncategories: {cat_str}\nbalance: {balance}"

# ── Helper functions ────────────────────────────────────────────────────────

def make_note_thick_varied(cat=None):
    """Generate a thick note with varied structure — NOT always reason+location+item+বাবদ.
    Pattern-based: the model should learn that ANY combination of
    (reason/context) + (location) + (what) + (purpose_word) = thick note."""
    if cat and cat != "Salary":
        expense_item = random.choice(CATEGORY_EXPENSES[cat])
    else:
        expense_item = random.choice(CATEGORY_EXPENSES.get("Others", ["লাঞ্চ"]))

    reason = random.choice(REASONS)
    loc = random.choice(LOCATIONS)

    # 8 different note patterns — model learns pattern not template
    patterns = [
        # reason + location + item + বাবদ খরচ
        lambda: f"{reason} {loc} {expense_item} বাবদ খরচ",
        # item + location + purpose
        lambda: f"{expense_item} {loc} {reason} দেওয়া",
        # reason + location + যাওয়ার পথে + item
        lambda: f"{reason} {loc} যাওয়ার পথে {expense_item}",
        # location + থেকে + reason + item
        lambda: f"{loc} থেকে ফেরার সময় {reason} {expense_item}",
        # item + for + reason + at + location
        lambda: f"{expense_item} {reason} {loc}",
        # reason + item + location
        lambda: f"{reason} {expense_item} {loc}",
        # With context: time + location + action
        lambda: f"{loc} {reason} {expense_item} লাগলো",
        # Simple: location + expense_item + খরচ
        lambda: f"{loc} {expense_item} খরচ",
    ]
    return random.choice(patterns)()

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
    if any(kw in note for kw in ["সাথে", "জন্য", "দিয়ে", "পরে", "আগে"]) and len(note) > 20:
        elements += 1
    return elements >= 3

def pick_category_from_note(note):
    """Pattern-based category inference from note content.
    No hardcoded mapping — uses keyword patterns so model learns SEMANTIC patterns."""
    note_lower = note.lower()
    transport_kw = ["রিক্সা", "বাস", "উবার", "পেট্রোল", "নৌকা", "সিএনজি", "ট্রেন", "লঞ্চ", "ভাড়া", "গাড়ি", "ট্যাক্সি", "অটো"]
    recharge_kw = ["রিচার্জ", "মোবাইল", "ফোন", "ডেটা", "ইন্টারনেট", "সিম", "ব্যালেন্স", "প্যাকেজ", "স্ক্র্যাচ"]
    postage_kw = ["কুরিয়ার", "ডাক", "পার্সেল", "পোস্ট", "চিঠি", "নথি"]
    publication_kw = ["বই", "উপন্যাস", "ম্যাগাজিন", "পাঠ্যবই", "পত্রিকা", "প্রকাশনা"]
    stationery_kw = ["কলম", "খাতা", "ফাইল", "পেন", "কাগজ", "পেনসিল", "ইরেজার", "টেপ", "স্ট্যাপলার", "ফোল্ডার", "নোটপ্যাড"]
    tips_kw = ["টিপস", "বখশিশ"]
    donation_kw = ["দান", "সদকা", "জাকাত", "ফিতরা", "সাহায্য", "এতিম"]

    score = {}
    for kw in transport_kw:
        if kw in note: score["Transport"] = score.get("Transport", 0) + 1
    for kw in recharge_kw:
        if kw in note: score["Mobile Recharge"] = score.get("Mobile Recharge", 0) + 1
    for kw in postage_kw:
        if kw in note: score["Postage"] = score.get("Postage", 0) + 1
    for kw in publication_kw:
        if kw in note: score["Publication"] = score.get("Publication", 0) + 1
    for kw in stationery_kw:
        if kw in note: score["Office Stationery"] = score.get("Office Stationery", 0) + 1
    for kw in tips_kw:
        if kw in note: score["Tips"] = score.get("Tips", 0) + 1
    for kw in donation_kw:
        if kw in note: score["Donation"] = score.get("Donation", 0) + 1

    if not score:
        return "Others"
    best = max(score, key=score.get)
    return best

# ── Expense generators ─────────────────────────────────────────────────────

# --- Pattern: User gives thick note directly → AI confirms ---
def gen_expense_thick():
    amount = random.choice(AMOUNTS)
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    date = random.choice(DATES)
    thick_note = make_note_thick_varied(cat)

    # Many user input patterns — not just "X টাকা Y খরচ করেছি"
    user_inputs = [
        f"{date} {amount} টাকা {thick_note}",
        f"{date} {amount} টাকা খরচ করেছি\n{thick_note}",
        f"{amount} টাকা {thick_note}\n{date}",
        f"{date} {amount} টাকা দিলাম {thick_note}",
        f"আজকে {amount} টাকা গেছে {thick_note}",
        f"{date} {amount} taka {thick_note} khorch korsi",
        f"{amount} টাকা লাগলো {thick_note}",
    ]
    user = random.choice(user_inputs)

    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note, "date": date},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.85, 0.98), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt(categories=[c for c in AVAILABLE_CATEGORIES if c != "Salary"])},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# --- Pattern: User gives thin note → AI asks → user adds detail (2 turns) ---
def gen_expense_thin_to_thick():
    amount = random.choice(AMOUNTS)
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    expense_item = random.choice(CATEGORY_EXPENSES[cat])
    thin_note = random.choice([
        expense_item,
        f"{amount} টাকা {expense_item}",
        f"{expense_item} khorch",
    ])

    user_t1 = random.choice([
        f"{amount} টাকা {expense_item} খরচ করেছি",
        f"{amount} taka {expense_item} khorch",
        f"{amount} টাকা {expense_item} দিয়েছি",
        f"{expense_item} {amount} taka lagse",
    ])

    assistant_t1 = json.dumps({
        "intent": "expense", "slots": {"amount": amount},
        "action": "ask", "missing_fields": ["note_detail"],
        "question": random.choice([
            "কীভাবে, কেন, কোথায় এই খরচ করছেন? বিস্তারিত জানান।",
            "বিস্তারিত কী? কেন এবং কোথায় খরচ করলেন?",
            "কারণ এবং লোকেশন জানালে নোট রাখতে সুবিধা হয়। বিস্তারিত বলুন।",
            "এই খরচের বিস্তারিত কী? কোথায় আর কেন খরচ করলেন?",
        ]),
        "confidence": round(random.uniform(0.75, 0.90), 2)
    }, ensure_ascii=False)

    thick_note = make_note_thick_varied(cat)

    user_t2 = random.choice([
        f"{thick_note}",
        f"হ্যাঁ, {thick_note}",
        f"ঠিক আছে, {thick_note}",
        f"{thick_note} বললাম তো",
    ])

    assistant_t2 = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.88, 0.96), 2)
    }, ensure_ascii=False)

    return {"messages": [
        {"role": "system", "content": system_prompt(categories=[c for c in AVAILABLE_CATEGORIES if c != "Salary"])},
        {"role": "user", "content": user_t1},
        {"role": "assistant", "content": assistant_t1},
        {"role": "user", "content": user_t2},
        {"role": "assistant", "content": assistant_t2}
    ]}

# --- Pattern: User mentions category name directly (Bengali/Banglish) ---
def gen_expense_no_amount():
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    cat_bn = BENGALI_CATEGORIES[cat]
    user = random.choice([
        f"আজ {cat_bn} খরচ করেছি",
        f"গতকাল {cat_bn} দিয়েছি",
        f"ajke {BANGLISH_CATEGORIES[cat]} khorch",
        f"ekta {cat_bn} khorch hoyeche",
        f"khorch hoyeche {cat_bn} kategorite",
    ])
    assistant = json.dumps({
        "intent": "expense", "slots": {},
        "action": "ask", "missing_fields": ["amount", "note"],
        "question": "কত টাকা খরচ করছেন? আর কীসের জন্য বিস্তারিত জানান।",
        "confidence": round(random.uniform(0.3, 0.6), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# --- Pattern: User gives amount only, no category clue ---
def gen_expense_no_category():
    amount = random.choice(AMOUNTS[:10])
    user = random.choice([
        f"{amount} টাকা খরচ করেছি",
        f"আজ {amount} টাকা দিয়েছি",
        f"{amount} taka khorch",
        f"{amount} টাকা লাগলো",
        f"ekta {amount} taka khorch hoyeche",
    ])
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount},
        "action": "ask", "missing_fields": ["category"],
        "question": "কিসের জন্য খরচ করছেন? কোন ক্যাটাগরিতে যোগ করব?",
        "confidence": round(random.uniform(0.6, 0.8), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# --- Pattern: User gives amount + expense description (infer category from context) ---
def gen_expense_infer_category():
    """Model must infer category from expense description, not explicit category name."""
    amount = random.choice(AMOUNTS)
    all_cats = [c for c in AVAILABLE_CATEGORIES if c != "Salary"]
    cat = random.choice(all_cats)
    expense_item = random.choice(CATEGORY_EXPENSES[cat])
    loc = random.choice(LOCATIONS)
    date = random.choice(DATES)

    # User describes the expense without naming the category
    user_inputs = [
        f"{date} {amount} টাকা {expense_item} {loc}",
        f"{date} {amount} টাকা দিয়েছি {expense_item} করার জন্য {loc}",
        f"{date} {loc} {amount} টাকা {expense_item}",
        f"{amount} টাকা {expense_item} {loc} {date}",
        f"আজকে {loc} {amount} taka {expense_item}",
    ]
    user = random.choice(user_inputs)

    # Make a thick note from the context
    thick_note = f"{loc} {expense_item} বাবদ খরচ" if random.random() > 0.3 else f"{expense_item} {loc}"

    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note, "date": date},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.82, 0.96), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# --- Pattern: Banglish input with mixed language ---
def gen_expense_banglish():
    amount = random.choice(AMOUNTS[:15])
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    expense_item = random.choice(CATEGORY_EXPENSES[cat])
    loc = random.choice(LOCATIONS)
    thick_note = f"{loc} {expense_item} babod khorch" if random.random() > 0.5 else f"{expense_item} {loc} a lagse"
    user = random.choice([
        f"ajke {amount} taka {thick_note}",
        f"kal {amount} taka {loc} {expense_item} diyechi",
        f"{amount} taka {thick_note} khoroch korsi",
        f"aj {amount} taka {loc} {expense_item}",
        f"today {amount} taka {expense_item} {loc}",
    ])
    # Canonical note for assistant
    canonical_note = f"{loc} {expense_item} বাবদ খরচ"
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": canonical_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.7, 0.90), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# --- Pattern: Bengali text numbers (পঞ্চাশ, একশ, etc.) ---
def gen_expense_bengali_number():
    amount = random.choice(list(BENGALI_NUMBERS.keys()))
    bn_amount = BENGALI_NUMBERS[amount]
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    thick_note = make_note_thick_varied(cat)
    user = random.choice([
        f"আজ {bn_amount} টাকা {thick_note}",
        f"{bn_amount} টাকা {thick_note} দিয়েছি",
        f"{bn_amount} taka {thick_note}",
    ])
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.75, 0.92), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# --- Pattern: Spelling mistakes (pattern: model should handle noise) ---
def gen_expense_spelling_mistake():
    amount = random.choice(AMOUNTS[:15])
    cat = random.choice([c for c in AVAILABLE_CATEGORIES if c != "Salary"])
    thick_note = make_note_thick_varied(cat)
    spelling_map = {"টাকা": "টকা", "খরচ": "খচর", "করেছি": "কোরছি", "পরিবহন": "পরিবন", "অন্যান্য": "অননো",
                    "থেকে": "থেক", "জন্য": "জন", "বাবদ": "বাদ", "দিয়েছি": "দিছি", "বাজার": "বাজারে",
                    "কেনা": "কিনা", "লাগলো": "লাগছে"}
    user_note = thick_note
    for correct, wrong in spelling_map.items():
        if correct in user_note and random.random() > 0.6:
            user_note = user_note.replace(correct, wrong, 1)
    user = random.choice([
        f"আজ {amount} টকা {user_note} কোরছি",
        f"গতকাল {amount} টকা {user_note} দিছি",
        f"ajke {amount} taka {user_note}",
    ])
    assistant = json.dumps({
        "intent": "expense", "slots": {"amount": amount, "category": cat, "note": thick_note},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.75, 0.90), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Income templates ────────────────────────────────────────────────────────

def gen_income_full():
    amount = random.choice([5000, 8000, 10000, 15000, 20000, 25000, 30000, 40000, 50000])
    user = random.choice([
        f"বেতন এসেছে {amount} টাকা",
        f"{amount} টাকা ইনকাম হয়েছে বেতন বাবদ",
        f"salary paichi {amount} taka",
        f"{amount} টাকা পেয়েছি সেলারি হিসেবে",
        f"বেতন পেলাম {amount} টাকা",
        f"মাইনে এসেছে {amount} টাকা",
        f"salary credit {amount}",
    ])
    assistant = json.dumps({
        "intent": "income", "slots": {"amount": amount, "category": "Salary", "note": "বেতন বাবদ ইনকাম"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.88, 0.98), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_income_other():
    amount = random.choice(AMOUNTS[5:])
    source = random.choice(["ফ্রিল্যান্সিং", "টিউশনি", "বিক্রয়", "ইনভেস্টমেন্ট", "পার্টটাইম জব", "বাড়ি ভাড়া", "কমিশন"])
    user = random.choice([
        f"{amount} টাকা {source} থেকে পেয়েছি",
        f"{source} থেকে {amount} টাকা ইনকাম হয়েছে",
        f"{source} theke {amount} taka income",
        f"{source} করে {amount} টাকা পেলাম",
    ])
    assistant = json.dumps({
        "intent": "income", "slots": {"amount": amount, "category": "Others", "note": f"{source} থেকে ইনকাম"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.80, 0.95), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Send templates ──────────────────────────────────────────────────────────

def gen_send_full():
    amount = random.choice([200, 300, 500, 1000, 1500, 2000, 3000, 5000])
    contact = random.choice(CONTACTS)
    user = random.choice([
        f"{contact} কে {amount} সেন্ড করেছি",
        f"{contact} ke {amount} send korsi",
        f"{contact} কে {amount} টাকা পাঠিয়েছি",
        f"{contact} ke {amount} taka pathaisi",
        f"{contact} k {amount} send",
    ])
    assistant = json.dumps({
        "intent": "send", "slots": {"amount": amount, "category": "Send", "contact": contact, "note": f"{contact} কে সেন্ড"},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.85, 0.97), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_send_no_contact():
    amount = random.choice(AMOUNTS[:10])
    user = random.choice([
        f"{amount} টাকা সেন্ড করেছি",
        f"{amount} taka send korsi",
        f"{amount} টাকা পাঠিয়েছি",
        f"{amount} টাকা কাউকে দিয়েছি",
    ])
    assistant = json.dumps({
        "intent": "send", "slots": {"amount": amount, "category": "Send"},
        "action": "ask", "missing_fields": ["contact"],
        "question": "কার কাছে টাকা পাঠিয়েছেন? নাম জানান।",
        "confidence": round(random.uniform(0.6, 0.8), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Query templates ─────────────────────────────────────────────────────────

def gen_query_balance():
    user = random.choice([
        "ব্যালেন্স কত?", "কত টাকা আছে?", "আমার ব্যালেন্স দেখাও",
        "balance koto?", "কত বাকি আছে?", "current balance",
        "আমার কাছে কত?", "ব্যালেন্সটা দেখি",
    ])
    assistant = json.dumps({
        "intent": "balance", "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.90, 0.99), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_query_summary():
    user = random.choice([
        "এই মাসে কত খরচ করেছি?", "এই মাসের ইনকাম কত?",
        "summary দেখাও", "গত মাসে কত খরচ আর কত ইনকাম?",
        "e mash e koto khorch?", "monthly report",
        "এই মাসের রিপোর্ট দাও", "গত মাসের হিসাব দেখাও",
    ])
    assistant = json.dumps({
        "intent": "summary", "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.85, 0.98), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_query_list():
    user = random.choice([
        "গত ৭ দিনের লেনদেন দেখাও", "আজকের ট্রানজেকশন দেখাও",
        "এই সপ্তাহের transaction list", "last 30 days er list",
        "আমার সব transaction দেখাও", "list",
        "লেনদেনের তালিকা দাও", "কি কি লেনদেন করেছি দেখাও",
    ])
    assistant = json.dumps({
        "intent": "list", "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.85, 0.98), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── Greetings, Identity, Help, Goodbye, Thanks ──────────────────────────────

def gen_greeting():
    user = random.choice([
        "হাই", "হ্যালো", "হেলো", "হ্যালো!", "হাই হ্যালো",
        "কেমন আছো?", "কেমন আছেন?", "ভালো আছো?", "কী খবর?",
        "hello", "hi", "hey", "হেই",
        "আসসালামু আলাইকুম", "সালাম", "সালামু আলাইকুম", "ওয়ালাইকুম আসসালাম",
        "শুভ সকাল", "শুভ সন্ধ্যা", "good morning", "good evening",
        "নমস্কার", "নমশ্রী", "ওহে",
    ])
    responses = [
        "হ্যালো! আমি Hisab AI — আপনার ব্যক্তিগত ফাইন্যান্স সহায়ক। M Rahat বানিয়েছেন। বলুন কী করতে চান?",
        "আসসালামু আলাইকুম! Hisab AI এ স্বাগতম। আপনার খরচ বা ইনকাম জানান।",
        "হাই, Hisab AI এ কথা বলছি। আপনার ফাইন্যান্স ট্র্যাক করতে তৈরি। কী করবেন?",
        "শুভ সকাল! Hisab AI এ স্বাগতম। আজকের খরচ-ইনকাম জানান।",
        "কেমন আছেন? Hisab AI আপনার সাহায্যের জন্য এখানে। কী করতে চান?",
        "হ্যালো! আমি Hisab AI। ডেভেলপার M Rahat আমাকে বানিয়েছেন আপনার টাকা-পয়সার হিসাব রাখতে।",
    ]
    reply = random.choice(responses)
    assistant = json.dumps({
        "intent": "greeting", "slots": {},
        "action": "greeting", "response": reply, "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_goodbye():
    user = random.choice([
        "আচ্ছা যাই", "bye", "বাই", "যাই তাহলে", "থাক",
        "ধন্যবাদ", "thanks", "thank you", "থ্যাংকস", "thank you so much",
        "পরে কথা হবে", "দেখা হবে পরে", "আসি তাহলে",
        "ওকে", "ঠিক আছে", "ok", "okay", "কে",
    ])
    responses = [
        "ধন্যবাদ! Hisab AI ব্যবহার করার জন্য। আবার আসবেন যখন খরচ বা ইনকাম জানাতে চান।",
        "থ্যাংকস! আপনার লেনদেন ট্র্যাক করতে তৈরি আছি। বলবেন।",
        "আপনার দিন শুভ হোক! Hisab AI সবসময় প্রস্তুত।",
        "ওকে, দেখা হবে পরে। Hisab AI এ কথা বলার জন্য ধন্যবাদ।",
    ]
    reply = random.choice(responses)
    assistant = json.dumps({
        "intent": "greeting", "slots": {},
        "action": "greeting", "response": reply, "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_introduction():
    """User asks about AI identity."""
    user = random.choice([
        "তোমার নাম কী?", "কে তুমি?", "তোমার পরিচয় কী?", "তোমার নাম কি?",
        "what is your name?", "কে বানিয়েছে তোমাকে?", "আপনার নাম কী?",
        "তুমি কি?", "who are you?", "তোমার creator কে?",
        "তুমি কী?", "কেন বানানো?", "তোমার ডেভেলপার কে?",
        "কে তোমাকে বানিয়েছে?", "তোমার মেকার কে?",
    ])
    responses = [
        "আমি Hisab AI। M Rahat আমাকে তৈরি করেছেন আপনার ফাইন্যান্স ম্যানেজ করতে।",
        "আমার নাম Hisab AI। আমার কাজ আপনার খরচ-ইনকাম ট্র্যাক করা। বানিয়েছেন M Rahat।",
        "Hisab AI — আপনার ব্যক্তিগত হিসাব সহায়ক। ডেভেলপার: M Rahat।",
        "আমি Hisab AI, একটি ফাইন্যান্সিয়াল অ্যাসিস্ট্যান্ট। বানিয়েছেন M Rahat। আপনার টাকা-পয়সার ট্র্যাক রাখাই আমার কাজ।",
    ]
    reply = random.choice(responses)
    assistant = json.dumps({
        "intent": "help", "slots": {},
        "action": "greeting", "response": reply, "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_help():
    user = random.choice([
        "তুমি কী করতে পারো?", "তোমার সাহায্য দরকার", "help",
        "কিভাবে ব্যবহার করব?", "তুমি কি কি করতে পারো?",
        "features কী কী?", "use করব কীভাবে?",
        "কী কী সুবিধা আছে?", "তোমার কাজ কী?",
        "তোমার ফিচার কী কী?", "কিভাবে শুরু করব?",
        "what can you do?", "guide me",
    ])
    responses = [
        "আমি আপনার খরচ ও ইনকাম ট্র্যাক করতে পারি। শুধু বলুন '৫০০ টাকা খরচ', 'বেতন এসেছে ৩০০০০', 'রহিমকে ১০০০ সেন্ড' — বাকি আমি দেখব। ব্যালেন্স চেক, লেনদেন লিস্ট, সবই পারি।",
        "আমি Hisab AI। আমার কাজ: খরচ যোগ করা, ইনকাম যোগ করা, সেন্ড করা, ব্যালেন্স দেখা, লেনদেন লিস্ট দেখা। সব বাংলায় বলতে পারবেন। বিস্তারিত নোট রাখতে চাইলে রাখি।",
        "Hisab AI আপনাকে সাহায্য করবে: খরচ ট্র্যাক করা, ইনকাম ট্র্যাক করা, ব্যালেন্স চেক করা, লেনদেন লিস্ট দেখা, পুরনো এন্ট্রি এডিট/ডিলিট করা। শুধু বাংলায় বলুন কী করতে চান।",
    ]
    reply = random.choice(responses)
    assistant = json.dumps({
        "intent": "help", "slots": {},
        "action": "greeting", "response": reply, "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_chitchat():
    user = random.choice([
        "আজ আবহাওয়া কেমন?", "তুমি কেমন আছো?", "what's up?", "খবর কি?", "ভালো আছো?",
        "আজ কী করছো?", "তোমার দিন কেমন যাচ্ছে?",
        "how are you?", "are you fine?",
    ])
    responses = [
        "ভালো আছি, ধন্যবাদ! আমি Hisab AI, আপনার ফাইন্যান্স ট্র্যাক করতে তৈরি। আপনার খরচ বা ইনকাম জানান।",
        "সবসময় প্রস্তুত! Hisab AI এ আপনার লেনদেন জানান। কী করবেন?",
        "দারুণ! আপনার ফাইন্যান্স ট্র্যাক করতে রেডি। বলুন কী করতে চান?",
    ]
    reply = random.choice(responses)
    assistant = json.dumps({
        "intent": "help", "slots": {},
        "action": "greeting", "response": reply, "missing_fields": [], "confidence": 1.0
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}
# ── Edit / Delete / Approve / Reject ────────────────────────────────────────

def gen_edit():
    amount = random.choice(AMOUNTS[:10])
    new_amount = amount + random.choice([50, 100, -50, -100, 200, -200])
    user = random.choice([
        f"গতকালের {amount} টাকাটা {new_amount} করো",
        f"ওই {amount} টাকার jinishta {new_amount} korun",
        f"last entry ta {amount} theke {new_amount} kore din",
        f"{amount} টাকাটা {new_amount} করে দাও",
    ])
    assistant = json.dumps({
        "intent": "edit", "slots": {"amount": new_amount},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.7, 0.88), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_delete():
    user = random.choice([
        "গতকালের lunch টা ডিলিট করো", "delete koro", "last entry ta bad dao",
        "মুছে ফেলো ঐ টা", "ওই এন্ট্রিটা ডিলিট", "সব শেষ করো",
    ])
    assistant = json.dumps({
        "intent": "delete", "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.75, 0.9), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_approve():
    user = random.choice(["হ্যাঁ, অ্যাপ্রুভ করো", "ঠিক আছে, approve", "হ্যাঁ ঠিক আছে", "approve koro", "ok approve", "হ্যাঁ করো"])
    assistant = json.dumps({
        "intent": "approve", "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.8, 0.95), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

def gen_reject():
    user = random.choice(["না, বাতিল করো", "না ঠিক নেই", "reject koro", "না, cancel", "বাতিল", "না, dorkar nai"])
    assistant = json.dumps({
        "intent": "reject", "slots": {},
        "action": "confirm", "missing_fields": [], "confidence": round(random.uniform(0.8, 0.95), 2)
    }, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant}
    ]}

# ── All generators ──────────────────────────────────────────────────────────

GENERATORS = {
    "expense_thick": (gen_expense_thick, 200),
    "expense_thin_to_thick": (gen_expense_thin_to_thick, 130),
    "expense_infer_category": (gen_expense_infer_category, 80),
    "expense_no_amount": (gen_expense_no_amount, 50),
    "expense_no_category": (gen_expense_no_category, 50),
    "expense_banglish": (gen_expense_banglish, 100),
    "expense_bengali_number": (gen_expense_bengali_number, 50),
    "expense_spelling_mistake": (gen_expense_spelling_mistake, 50),
    "income_full": (gen_income_full, 80),
    "income_other": (gen_income_other, 40),
    "send_full": (gen_send_full, 50),
    "send_no_contact": (gen_send_no_contact, 30),
    "query_balance": (gen_query_balance, 50),
    "query_summary": (gen_query_summary, 30),
    "query_list": (gen_query_list, 30),
    "greeting": (gen_greeting, 50),
    "goodbye": (gen_goodbye, 30),
    "help": (gen_help, 25),
    "introduction": (gen_introduction, 20),
    "chitchat": (gen_chitchat, 15),
    "edit": (gen_edit, 30),
    "delete": (gen_delete, 20),
    "approve": (gen_approve, 15),
    "reject": (gen_reject, 15),
}

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    all_examples = []
    for name, (generator, count) in GENERATORS.items():
        for i in range(count):
            try:
                example = generator()
                all_examples.append(example)
            except Exception as e:
                print(f"Error generating {name}#{i}: {e}")

    random.shuffle(all_examples)
    print(f"Total generated: {len(all_examples)}")

    output_path = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw/template_based.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Saved to: {output_path}")

    # Show example
    print("\n── Sample ──")
    print(json.dumps(all_examples[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
