# Friday

A smart AI assistant who remembers everything about you.

Friday is a desktop chat assistant built in Python on top of the Google Gemini API. Unlike a normal chatbot, it keeps a persistent memory of the person it talks to. It decides what is worth remembering, stores it on disk, and brings the right memories back into every conversation so replies feel personal and consistent across sessions.

## What Friday Can Do

1. Chat through a simple desktop window built with Tkinter.
2. Remember important things you say, and carry them across sessions.
3. Score each message for importance on a scale of 1 to 10 and sort it into a category such as personality, relationship, interests, emotions, productivity, romance, social or academic.
4. Retrieve the most relevant memories for each new message and add them to the prompt as context.
5. Review the conversation every few exchanges and extract new facts for long term memory.
6. Keep track of unfinished topics, for example when you say you will talk about something later.
7. Greet you based on the time of day and remind you what the last conversation was about.
8. Save facts on command. Typing `rem:` followed by a fact stores it directly in your profile.
9. Fall back to a live web search through SerpAPI when the model signals that it is unsure.

## How the Memory System Works

Every message you send goes through a small pipeline.

1. Friday asks Gemini what the message reveals about your personality, interests or habits, and turns it into a short memory insight.
2. A second prompt gives that insight an importance score from 1 to 10, and a third assigns it a category.
3. Memories with a score of 6 or higher are written to `longterm_memory.json`.
4. Memories with a score of 4 or 5, and any message containing cues such as "talk later" or "remind", go to `incomplete_memory.json`.
5. When you start Friday, a summary of long term memory is sent to the model so the conversation begins with context.
6. For each new message, Friday compares it with stored memories using text similarity, picks the top three matches above a threshold, and adds them to the prompt.
7. After every five exchanges, Friday reviews the recent conversation and saves one to three new facts.

## Project Structure

main.py: Starts the app, builds the Tkinter chat window, and connects the chat loop to Gemini and the memory system.

brain.py: The core logic. Handles prompting, importance scoring, categorization, memory saving, memory matching, summaries and greetings.

identity.py: Loads and saves the user profile and handles the `rem:` command.

internet.py: Web search fallback using SerpAPI, with a monthly usage counter.

llama_wrapper.py: An optional wrapper for running a local Llama 3 model through Ollama.

setup_jsons.py: Makes sure the memory and profile files exist on first run.

longterm_memory.json: Stored important memories.

incomplete_memory.json: Memories for unfinished or lower importance topics.

profile.json: Name, preferred title, nicknames and custom facts.

search_usage.json: Tracks how many web searches have been used.

requirements.txt: Python dependencies.

## Getting Started

### Requirements

Python 3.10 or newer, a Gemini API key from Google AI Studio, and optionally a SerpAPI key for web search.

### Installation

1. Clone the repository.

```
git clone https://github.com/USI-27/Friday.git
cd Friday
```

2. Install the dependencies listed in requirements.txt.

```
pip install -r requirements.txt
```

3. Create a file named `.env` in the project folder and add your keys.

```
GEMINI_API_KEY=your_gemini_key_here
SERPAPI_KEY=your_serpapi_key_here
```

The SerpAPI key is optional. Without it, Friday simply tells you that web search is unavailable.

4. Run the assistant.

```
python main.py
```

### Using Friday

Type a message in the box and press Enter or click Send. To save a fact directly, start your message with `rem:`, for example `rem: I prefer studying at night`. To end the session, say something like "bye" or "quit".

## Security Note

Never commit your `.env` file. Keep it listed in `.gitignore` so your API keys stay private. The memory files contain personal information from your conversations, so treat them as private too.

## Current Limitations

1. Memory matching uses simple text similarity from Python's difflib, so it can miss memories that mean the same thing but use different words.
2. Memories are stored in JSON files, which suits one user but does not scale to many users.
3. There is no way yet to update, merge or forget old memories automatically.

## Roadmap

1. Replace text similarity with embeddings and vector search for better recall.
2. Add memory updating, merging and forgetting so stored facts stay accurate over time.
3. Move storage from JSON files to a database.
4. Add evaluations that measure recall quality, cost and latency.
5. Expose Friday's memory as tools that other AI agents can call.

## Tech Stack

Python, Google Gemini API, Tkinter, SerpAPI, Ollama (optional), JSON storage.

## Author

Udbhav Singh. GitHub: https://github.com/USI-27
