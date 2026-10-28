import json
import os

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def migrate_memory_format():
    path = "longterm_memory.json"
    memory = load_json(path)
    updated = []

    for m in memory:
        original = m["text"].strip()
        text = original

        # Change "User: ..." or "Friday: ..." to arrow format
        if text.startswith("User: "):
            text = text.replace("User: ", "User → ", 1)
        elif text.startswith("Friday: "):
            text = text.replace("Friday: ", "Friday → ", 1)

        # Remove bullet (* ) but preserve casing
        if text.startswith("* "):
            text = text[2:].strip()

        # Only update if something changed
        if text != original:
            print(f"🔁 Updated:\n  Old: {original}\n  New: {text}\n")

        m["text"] = text
        updated.append(m)

    save_json(path, updated)
    print("✅ Migration complete: Arrow conversion and cleanup done.")

if __name__ == "__main__":
    migrate_memory_format()
