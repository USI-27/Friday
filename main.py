import os
import sys
import time
import threading
import google.generativeai as genai
from dotenv import load_dotenv
from brain import update_memory, summarize_longterm_memory
from identity import handle_remember_command
from setup_jsons import ensure_memory_files
from brain import review_and_summarize_memory
from datetime import datetime
from brain import get_greeting_message, get_nudge_message
import tkinter as tk
from tkinter import scrolledtext

# -------------------------------
# Original code setup
# -------------------------------
recent_chat = []
REVIEW_EVERY = 5
ensure_memory_files()

# Load API key and initialize Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()

exit_phrases = ["exit", "quit", "goodbye", "bye", "see you", "i'm done", "ttyl"]

def is_exit_phrase(text):
    return any(phrase in text.lower() for phrase in exit_phrases)

def discord_typing_animation(stop_event):
    dots = ["   ", ".  ", ".. ", "..."]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write("\rFRIDAY is typing" + dots[i % len(dots)])
        sys.stdout.flush()
        time.sleep(0.4)
        i += 1
    sys.stdout.write("\r" + " " * 30 + "\r")

def friday_say(text):
    stop_event = threading.Event()
    t = threading.Thread(target=discord_typing_animation, args=(stop_event,))
    t.start()
    base_delay = 0.5
    msg_delay = min(2.5, len(text) * 0.01)
    time.sleep(base_delay + msg_delay)
    stop_event.set()
    t.join()
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.015 if len(text) < 100 else 0.008)
    print()

# -------------------------------
# GUI setup
# -------------------------------
root = tk.Tk()
root.title("FRIDAY AI Assistant")
root.geometry("650x500")

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 11))
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.tag_config("user", foreground="blue")
chat_area.tag_config("friday", foreground="green")

entry = tk.Text(root, height=3, font=("Arial", 11))
entry.pack(padx=10, pady=(0, 10), fill=tk.X)

def append_message(sender, message, tag):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"{sender}: {message}\n", tag)
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)

# Inject greeting + nudge in GUI
append_message("FRIDAY", get_greeting_message(), "friday")
nudge = get_nudge_message()
if nudge:
    append_message("FRIDAY", nudge, "friday")

# Inject summary to start context
summary_prompt = summarize_longterm_memory()
chat.send_message(summary_prompt)

def send_prompt(event=None):
    prompt = entry.get("1.0", tk.END).strip()
    if not prompt:
        return
    entry.delete("1.0", tk.END)
    append_message("You", prompt, "user")

    if is_exit_phrase(prompt):
        append_message("FRIDAY", "Logging off. Take care boss 🫡", "friday")
        root.after(1500, root.destroy)
        return

    is_cmd, response = handle_remember_command(prompt)
    if is_cmd:
        append_message("FRIDAY", response, "friday")
        return

    def process():
        try:
            response_obj = chat.send_message(prompt)
            response_text = response_obj.text
            append_message("FRIDAY", response_text, "friday")

            update_memory(model, "user", prompt)
            update_memory(model, "friday", response_text)

            recent_chat.append({"role": "user", "text": prompt})
            recent_chat.append({"role": "friday", "text": response_text})

            if len(recent_chat) >= REVIEW_EVERY * 2:
                review_and_summarize_memory(model, recent_chat)
                recent_chat.clear()

        except Exception as e:
            append_message("FRIDAY", f"Something went wrong.\nError: {e}", "friday")

    threading.Thread(target=process).start()

entry.bind("<Return>", lambda e: (send_prompt(), "break"))
send_btn = tk.Button(root, text="Send", command=send_prompt, font=("Arial", 11))
send_btn.pack(pady=(0, 10))

root.mainloop()
