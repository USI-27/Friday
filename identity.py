import json
import os

PROFILE_FILE = "profile.json"

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)

def handle_remember_command(text):
    try:
        if not text.lower().startswith("rem:"):
            return False, None

        fact = text[len("rem:"):].strip() 
        profile = load_profile()

        if "custom_facts" not in profile:
            profile["custom_facts"] = []

        profile["custom_facts"].append(fact)
        save_profile(profile)

        return True, f"Got it boss, I’ll remember that: \"{fact}\""
    except Exception as e:
        return True, f"Oops, couldn’t remember that. Error: {e}"
