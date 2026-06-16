"""
Hisab Pata — Combine all raw datasets into train/test split
"""

import json, random, os

random.seed(42)

base = "/home/mrahat/Documents/HisabPata/AI Server/dataset"
raw_dir = os.path.join(base, "raw")

all_examples = []
for fname in ["template_based.jsonl", "multi_turn.jsonl", "edge_cases.jsonl"]:
    fpath = os.path.join(raw_dir, fname)
    with open(fpath) as f:
        lines = f.readlines()
    all_examples.extend([json.loads(l) for l in lines])
    print(f"Loaded {len(lines)} from {fname}")

random.shuffle(all_examples)
print(f"\nTotal: {len(all_examples)}")

# 90/10 split
split = int(len(all_examples) * 0.9)
train = all_examples[:split]
test = all_examples[split:]

print(f"Train: {len(train)}, Test: {len(test)}")

# Save validated versions
validated_dir = os.path.join(base, "validated")
with open(os.path.join(validated_dir, "train.jsonl"), "w") as f:
    for ex in train:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

with open(os.path.join(validated_dir, "test.jsonl"), "w") as f:
    for ex in test:
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")

print(f"\nSaved to {validated_dir}/")

# ── Summary stats ──
intents = {}
for ex in all_examples:
    for m in ex["messages"]:
        if m["role"] == "assistant":
            try:
                intent = json.loads(m["content"]).get("intent", "unknown")
                intents[intent] = intents.get(intent, 0) + 1
            except:
                pass

print("\n── Intent Distribution ──")
for intent, count in sorted(intents.items(), key=lambda x: -x[1]):
    print(f"  {intent}: {count} ({100*count/len(all_examples):.1f}%)")

# Multi-turn count
multi_turn = sum(1 for ex in all_examples if len(ex["messages"]) > 3)
print(f"\nMulti-turn conversations: {multi_turn}")
print(f"Single-turn examples: {len(all_examples) - multi_turn}")

# Banglish detection (heuristic: contains Latin chars)
banglish = 0
for ex in all_examples:
    for m in ex["messages"]:
        if m["role"] == "user" and any(c.isascii() for c in m["content"]) and any(c.isalpha() for c in m["content"] if c.isascii()):
            banglish += 1
            break
print(f"User messages with Banglish/English: {banglish} ({100*banglish/len(all_examples):.1f}%)")
