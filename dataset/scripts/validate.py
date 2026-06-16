"""
Hisab Pata — Dataset Validator
Checks: JSON parseable, schema valid, finance rules, note completeness
"""

import json, sys, os

VALID_INTENTS = {"expense", "income", "send", "balance", "summary", "list", "greeting", "help", "edit", "delete", "approve", "reject"}
VALID_ACTIONS = {"confirm", "ask", "greeting"}

errors = []
warnings = []

def check_example(ex, idx):
    msgs = ex.get("messages", [])
    if not msgs:
        errors.append(f"#{idx}: no messages")
        return

    # Check roles
    roles = [m["role"] for m in msgs]
    if roles[0] != "system":
        errors.append(f"#{idx}: first role must be system, got {roles[0]}")

    # Check assistant messages are valid JSON
    for m in msgs:
        if m["role"] == "assistant":
            try:
                content = json.loads(m["content"])
            except:
                errors.append(f"#{idx}: assistant content not valid JSON: {m['content'][:80]}")
                continue

            # Check intent
            intent = content.get("intent")
            if intent not in VALID_INTENTS:
                errors.append(f"#{idx}: invalid intent '{intent}'")

            # Check action
            action = content.get("action")
            if action not in VALID_ACTIONS:
                errors.append(f"#{idx}: invalid action '{action}'")

            # Check slots is a dict
            slots = content.get("slots", {})
            if not isinstance(slots, dict):
                errors.append(f"#{idx}: slots must be dict")

            # Check amount is numeric if present
            if "amount" in slots:
                amt = slots["amount"]
                if not isinstance(amt, (int, float)) or amt == 0:
                    # Zero is allowed only for edge cases
                    pass

            # Check note completeness for expense confirm
            if intent == "expense" and action == "confirm" and "note" in slots:
                note = slots["note"]
                elements = 0
                if any(kw in note for kw in ["ভাড়া","খরচ","লাঞ্চ","বাজার","দান","টিপস","রিচার্জ","কেনা"]):
                    elements += 1
                if any(kw in note for kw in ["জন্য","কারণ","কাজে","বাবদ","হেতু"]):
                    elements += 1
                if any(kw in note for kw in ["থেকে","যায়","গিয়ে"]):
                    elements += 1
                if len(note) > 30:
                    elements += 1
                if elements < 2:
                    warnings.append(f"#{idx}: thin note for confirm: '{note[:60]}' ({elements}/4 elements)")

            # Check missing_fields match ask action
            if action == "ask":
                if not content.get("missing_fields") and not content.get("question"):
                    warnings.append(f"#{idx}: ask action but no missing_fields or question")
            if action == "confirm":
                if content.get("missing_fields"):
                    warnings.append(f"#{idx}: confirm but has missing_fields")

            # Check confidence
            conf = content.get("confidence")
            if conf is not None:
                if not (0.0 <= conf <= 1.0):
                    errors.append(f"#{idx}: confidence out of range: {conf}")

            # Check send intent has contact
            if intent == "send" and action == "confirm":
                if "contact" not in slots:
                    errors.append(f"#{idx}: send confirm without contact")

    # Check that user messages are non-empty
    for i, m in enumerate(msgs):
        if m["role"] == "user" and not m["content"].strip():
            errors.append(f"#{idx}: empty user message at position {i}")

def main():
    base = "/home/mrahat/Documents/HisabPata/AI Server/dataset/raw"
    files = [
        os.path.join(base, "template_based.jsonl"),
        os.path.join(base, "multi_turn.jsonl"),
        os.path.join(base, "edge_cases.jsonl"),
    ]

    total = 0
    for fpath in files:
        if not os.path.exists(fpath):
            print(f"⚠ Skipping {fpath} (not found)")
            continue
        with open(fpath) as f:
            lines = f.readlines()
        print(f"📄 {os.path.basename(fpath)}: {len(lines)} examples")
        for i, line in enumerate(lines):
            try:
                ex = json.loads(line.strip())
                check_example(ex, f"{os.path.basename(fpath)}:{i}")
            except json.JSONDecodeError as e:
                errors.append(f"{os.path.basename(fpath)}:{i}: JSON parse error: {e}")
            total += 1

    print(f"\n{'='*40}")
    print(f"Total examples: {total}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print(f"\n❌ ERRORS:")
        for e in errors[:20]:
            print(f"  • {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more")

    if warnings:
        print(f"\n⚠ WARNINGS (sample):")
        for w in warnings[:15]:
            print(f"  • {w}")

    if not errors:
        print("\n✅ ALL VALID")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
