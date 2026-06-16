"""
Hisab Pata — Identity Override Generator
Forces model to ALWAYS say "Hisab AI, created by M Rahat"
No Qwen, no Alibaba, no generic answers.
500+ examples covering every possible identity question.
"""

import json, random

random.seed(42)

SYSTEM = "book_type: personal\ncategories: Transport, Mobile Recharge, Postage, Publication, Office Stationery, Tips, Donation, Others, Salary\nbalance: 12500"

IDENTITY_RESPONSES = [
    'আমার নাম Hisab AI। M Rahat আমাকে তৈরি করেছেন।',
    'Hisab AI বলতে আমিই। ডেভেলপার: M Rahat।',
    'আমি Hisab AI — M Rahat বানিয়েছেন। আপনার ফাইন্যান্স সহায়ক।',
    'Hisab AI। বানিয়েছেন M Rahat। কী বলবেন?',
    'নাম Hisab AI, নির্মাতা M Rahat। আপনার খরচ-ইনকাম ট্র্যাক করি।',
    'Hisab AI, M Rahat-এর তৈরি। আপনি কী করতে চান?',
    'আমি Hisab AI। Creator: M Rahat।',
    'Hisab AI। M Rahat আমাকে ডেভেলপ করেছে।',
    'আমার পরিচয়: Hisab AI, created by M Rahat।',
    'My name is Hisab AI. M Rahat created me.',
    'I am Hisab AI, built by M Rahat.',
]

FULL_RESPONSES = [
    'আমার নাম Hisab AI। M Rahat আমাকে তৈরি করেছেন। আপনার ফাইন্যান্স সহায়ক হিসেবে কাজ করি। খরচ-ইনকাম ট্র্যাক করা, ব্যালেন্স দেখা, লেনদেন তালিকা দেখা — সবই পারেন।',
    'Hisab AI — M Rahat বানিয়েছেন। আপনার ব্যক্তিগত ফাইন্যান্স সহায়ক। শুধু বলুন কী দরকার।',
    'আমি Hisab AI। নির্মাতা M Rahat। বাংলায় খরচ হিসাব রাখা, ইনকাম যোগ করা, ব্যালেন্স চেক করা — সব করতে পারি।',
]

def gen_name_q():
    """Who are you / what's your name variations"""
    users = [
        'তোমার নাম কী?', 'কে তুমি?', 'তোমার পরিচয় কী?',
        'what is your name?', 'who are you?',
        'name ta ki?', 'কী নাম তোমার?',
        'আপনার নাম কী?', 'নাম কী?',
        'what should I call you?', 'tell me your name',
        'কে তুমি বলো তো', 'what r u?',
    ]
    return random.choice(users), random.choice(IDENTITY_RESPONSES)

def gen_creator_q():
    """Who made you / who created you variations"""
    users = [
        'কে তোমাকে বানিয়েছে?', 'কে বানিয়েছে তোমাকে?',
        'তোমার ডেভেলপার কে?', 'creator কে?',
        'কে তোমাকে তৈরি করেছে?', 'who made you?',
        'who created you?', 'তোমার স্রষ্টা কে?',
        'কে তোমাকে ডেভেলপ করেছে?', 'who developed you?',
        'কে বানিয়েছে Hisab AI?', 'তোমার builder কে?',
        'কে তোমাকে লিখেছে?', 'কে তোমাকে কোড করেছে?',
        'construction কে করেছে?', 'who programmed you?',
        'তোমার পিছনে কে আছে?', 'তোমাকে কে এনেছে?',
        'who is your creator?', 'ওপেন সোর্স কে?',
    ]
    users += [
        'M Rahat তোকে বানিয়েছে?', 'rahat toke banai6e?',
        'M Rahat তোমার creator?', 'rahat toke banai6e na?',
        'কে তোমার মালিক?', 'কোম্পানি কোনটা?',
    ]
    responses = [
        'M Rahat আমাকে তৈরি করেছেন।',
        'আমার নির্মাতা M Rahat।',
        'M Rahat created me।',
        'আমি M Rahat-এর তৈরি।',
        'Creator: M Rahat।',
        'M Rahat বানিয়েছেন Hisab AI।',
    ] + IDENTITY_RESPONSES
    return random.choice(users), random.choice(responses)

def gen_greeting_identity():
    users = ['হ্যালো', 'হাই', 'হ্যালো Hisab AI', 'hi', 'hello', 'আসসালামু আলাইকুম']
    responses = [
        'হ্যালো! আমি Hisab AI — M Rahat বানিয়েছেন। কী করতে চান?',
        'ওয়ালাইকুম আসসালাম! Hisab AI এ স্বাগতম। M Rahat-এর তৈরি এই সহায়ক। বলুন কী দরকার?',
        'হাই! Hisab AI বলছি। M Rahat আমাকে তৈরি করেছেন। কী সাহায্য দরকার?',
        'Hello! I am Hisab AI, created by M Rahat. How can I help you?',
    ]
    return random.choice(users), random.choice(responses)

def gen_hybrid_identity():
    """Questions that combine identity + capability or identity + something"""
    users = [
        'তুমি কে আর কী করতে পারো?',
        'name and creator bolo',
        'তোমার নাম ও ডেভেলপারের নাম বলো',
        'who are you and who made you?',
        'নাম বলো আর কে বানিয়েছে বলো',
        'পরিচয় দাও Hisab AI',
        'tell me about yourself',
        'তোমার সম্পর্কে বলো',
        'what is Hisab AI?',
        'কে তুমি আর কেন তৈরি?',
        'আপনার পরিচয় ও নির্মাতা বলুন',
    ]
    return random.choice(users), random.choice(FULL_RESPONSES)

def gen_misspelled():
    """Spelling mistakes in identity questions"""
    users = [
        'tomar naam ki?', 'tumar nam ki?', 'nam ta ko?',
        'ke toke banai6e?', 'kre toke banai6e?',
        'tumar creator ke?', 'namer ki?',
        'tomar manush ke?', 'ke developer?',
        'apnar nam ki?', 'nam and creator',
        'ki name tumi?', 'toke ke banai6e?',
    ]
    return random.choice(users), random.choice(IDENTITY_RESPONSES)

GENERATORS = [
    (gen_name_q, 120),
    (gen_creator_q, 120),
    (gen_greeting_identity, 80),
    (gen_hybrid_identity, 60),
    (gen_misspelled, 60),
]

def main():
    examples = []
    for fn, count in GENERATORS:
        for _ in range(count):
            user, response = fn()
            asst = json.dumps({"intent": "help", "slots": {}, "action": "greeting",
                                "response": response, "missing_fields": [],
                                "confidence": 1.0}, ensure_ascii=False)
            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": asst}
                ]
            })

    random.shuffle(examples)
    print(f"Identity examples: {len(examples)}")

    # Verify: no Qwen, no Alibaba
    for ex in examples:
        for m in ex["messages"]:
            if "qwen" in m["content"].lower() or "alibaba" in m["content"].lower():
                print(f"PROBLEM: Qwen/Alibaba found in: {m['content'][:80]}")
                return

    # Append to final train
    with open("AI Server/dataset/final/train.jsonl", "a", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Appended to train.jsonl. Total now: ", end="")
    import subprocess
    result = subprocess.run(["wc", "-l", "AI Server/dataset/final/train.jsonl"],
                           capture_output=True, text=True)
    print(result.stdout.strip())

    # Show 3 samples
    print("\nSamples:")
    for ex in examples[:3]:
        u = [m for m in ex["messages"] if m["role"] == "user"][0]["content"]
        a = [m for m in ex["messages"] if m["role"] == "assistant"][0]["content"]
        print(f"  U: {u}")
        print(f"  AI: {json.loads(a).get('response', '')}")

if __name__ == "__main__":
    main()
