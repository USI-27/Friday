import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from identity import load_profile
from internet import search_web

MAIN_MEMORY = "longterm_memory.json"
INCOMPLETE_MEMORY = "incomplete_memory.json"

# -------------------------------
# Gemini Query Function
# -------------------------------
def query_gemini(model, prompt: str) -> str:
    try:
        resp = model.generate_content(prompt)
        return (resp.text or "").strip()
    except Exception as e:
        print("⚠️ Gemini query failed:", e)
        return "Sorry boss, my brain froze 🧊"

# -------------------------------
# File Helpers
# -------------------------------
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def extract_keywords(text):
    return [w for w in text.split() if len(w) > 4]

def detect_incomplete(text):
    cues = ["talk later", "continue", "remind", "come back", "later", "i'll tell"]
    return any(phrase in text.lower() for phrase in cues)

# -------------------------------
# Context Helpers
# -------------------------------
def get_current_time_context():
    now = datetime.now()
    hour = now.hour

    if hour < 5:
        mood = "early hours"
    elif hour < 12:
        mood = "morning"
    elif hour < 17:
        mood = "afternoon"
    elif hour < 21:
        mood = "evening"
    else:
        mood = "late night"

    return {
        "time_str": now.strftime("%Y-%m-%d %I:%M %p"),
        "mood": mood,
        "dow": now.strftime("%A")
    }

# -------------------------------
# Smart Prompt
# -------------------------------
def friday_smart_prompt(model, user_input, recent_history=None):
    if recent_history is None:
        recent_history = []
    matched_memory = match_memories_to(user_input)
    memory_block = f"\n🧠 Relevant Memory:\n{matched_memory}\n" if matched_memory else ""
    style = (
        "Respond confidently like a real human would. "
        "If you must fall back to web search, do it silently without disclaimers."
    )
    history_snip = "\n".join(
        [f"{m['role'].capitalize()} → {m['text']}" for m in recent_history[-6:]]
    )
    ctx = get_current_time_context()

    prompt = (
        f"{style}\n{history_snip}\n\n"
        f"As of {ctx['time_str']} on {ctx['dow']} ({ctx['mood']}), the following are the facts you know about him or the context "
        f"{memory_block}\n"
        f"Respond like a real human being would using memory facts and currently he is saying:\n"
        f"User → \"{user_input}\""
    )

    ai_response = query_gemini(model, prompt)

    red_flags = ["my knowledge cutoff", "i cannot access real-time"]
    if any(flag.lower() in ai_response.lower() for flag in red_flags):
        web_result = search_web(user_input)
        return f"FRIDAY: I wasn’t confident in my answer, so I looked it up for you, boss:\n\n{web_result}"

    return f"FRIDAY: {ai_response}"

# -------------------------------
# Memory Functions
# -------------------------------
def get_importance(model, text, history=[]):
    context = "\n".join([f"{m['role'].capitalize()} → {m['text']}" for m in history[-5:]])
    prompt = f"""
You are Friday, Udbhav Singh’s personal AI assistant. Your job is to assign an importance score (1–10) to a new message based on how useful it is for understanding Udbhav's personality, behavior, interests, or emotional life.

Scoring:
1 = Irrelevant banter
3 = Mildly interesting
5 = Somewhat useful detail
7 = Strong insight into values/interests
10 = Deep emotional/behavioral insight

Message: "{text}"

Recent context:
{context}

Respond with only a number 1–10.
"""
    try:
        response = query_gemini(model, prompt)
        score = int(response[0]) if response and response[0].isdigit() else 5
        return max(1, min(score, 10))
    except Exception as e:
        print("⚠️ Importance scoring failed:", e)
        return 5

def infer_user_preference(model, text):
    prompt = f"""
You are Friday, the personal AI assistant for Udbhav Singh.
Infer what his statement reveals about personality, mindset, interests, emotions, or values.
Respond only with the memory insight.

Message:
\"{text}\"
"""
    return query_gemini(model, prompt)

def get_memory_category(model, summary):
    prompt = f"""
Categorize this into one of:
personality, relationship, interests, emotions, productivity, romance, social, academic.

Message: "{summary}"

Respond only with the category name.
"""
    response = query_gemini(model, prompt).lower()
    categories = ["personality", "relationship", "interests", "emotions", "productivity", "romance", "social", "academic"]
    return response if response in categories else "misc"

def update_memory(model, role, text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if role == "friday":
        return

    arrow_text = f"{role.capitalize()} → {text.strip()}"
    summary = infer_user_preference(model, text)
    importance = get_importance(model, summary)
    category = get_memory_category(model, summary)

    entry = {
        "role": role,
        "text": summary,
        "source": arrow_text,
        "keywords": extract_keywords(summary),
        "importance": importance,
        "category": category,
        "time": timestamp
    }

    if detect_incomplete(text):
        data = load_json(INCOMPLETE_MEMORY)
        data.append(entry)
        save_json(INCOMPLETE_MEMORY, data)
        return

    if importance >= 6:
        data = load_json(MAIN_MEMORY)
        data.append(entry)
        save_json(MAIN_MEMORY, data)
    elif importance >= 4:
        data = load_json(INCOMPLETE_MEMORY)
        data.append(entry)
        save_json(INCOMPLETE_MEMORY, data)

# -------------------------------
# Memory Summary
# -------------------------------
def summarize_longterm_memory():
    profile = load_profile()
    data = load_json(MAIN_MEMORY)
    summary = f"You are Friday, AI assistant for {profile.get('name', 'Udbhav Singh')}.\n"
    summary += f"Address him as '{profile.get('title', 'boss')}' usually, or playful names like {', '.join(profile.get('nicknames', []))} when he's chill.\n\n"
    summary += "Here's what you remember:\n"
    for d in data:
        summary += f"- {d['text']}\n"
    return summary

def review_and_summarize_memory(model, recent_history):
    chat_history = "\n".join([f"{m['role'].capitalize()}: {m['text']}" for m in recent_history])
    prompt = f"""
You are Friday. Here is a recent segment of conversation:

{chat_history}

Extract 1–3 important memory facts that reflect:
- Preferences, personality, interests
- Emotional insights or habits
- Any new details for long-term memory

Respond ONLY with a bullet list.
"""
    try:
        response = query_gemini(model, prompt)
        lines = response.split("\n")
        memory_facts = [line.lstrip("-• ").strip() for line in lines if line.strip()]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        memory_data = load_json(MAIN_MEMORY)
        for fact in memory_facts:
            memory_data.append({
                "role": "reviewer",
                "text": fact,
                "keywords": extract_keywords(fact),
                "importance": 7,
                "time": timestamp
            })
        save_json(MAIN_MEMORY, memory_data)
    except Exception as e:
        print("⚠️ Friday memory review failed:", e)

# -------------------------------
# Greetings & Matching
# -------------------------------
def get_greeting_message():
    now = datetime.now()
    hour = now.hour
    if hour < 5:
        return "You're up early, boss. Ready for another nocturnal brainstorm?"
    elif hour < 12:
        return "Good morning, boss. I’m tuned in and caffeinated ☕"
    elif hour < 17:
        return "Good afternoon, boss. Systems green, energy clean."
    elif hour < 21:
        return "Evening, boss. Want to wrap the day or stir up some mischief?"
    else:
        return "Late night mode activated, boss. Let’s keep it quiet but brilliant. 🌙"

def get_nudge_message():
    longterm = load_json(MAIN_MEMORY)
    if not longterm:
        return ""
    last_text = longterm[-1]["text"]
    return f"(Just so you know, our last convo touched on: \"{last_text[:100]}...\")"

def match_memories_to(user_input, max_results=3):
    memories = load_json(MAIN_MEMORY)
    scored = []
    for m in memories:
        score = SequenceMatcher(None, user_input.lower(), m["text"].lower()).ratio()
        if score > 0.3:
            scored.append((score, m["text"]))
    top_matches = sorted(scored, reverse=True)[:max_results]
    return "\n".join([f"- {text}" for _, text in top_matches]) if top_matches else ""
