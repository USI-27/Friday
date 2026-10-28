import os
import json

def ensure_memory_files():
    files = {
        "longterm_memory.json": [],
        "incomplete_memory.json": [],
        "profile.json": {
            "name": "Udbhav Singh",
            "title": "boss",
            "nicknames": ["babe", "cutie", "pookie"],
            "interests": ["AI", "Python", "astrophotography"],
            "preferences": {
                "address_formal": True
            },
            "family": {
                "sister": "Gehna",
                "niece": "Leela"
            },
            "custom_facts": []
        }
    }

    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, "w") as f:
                json.dump(content, f, indent=4)
            print(f"✅ Created missing file: {filename}")
