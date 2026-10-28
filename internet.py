import os
import json
from serpapi import GoogleSearch

SEARCH_LOG_FILE = "search_usage.json"

# Load current count
def load_search_count():
    if not os.path.exists(SEARCH_LOG_FILE):
        return 0
    with open(SEARCH_LOG_FILE, "r") as f:
        return json.load(f).get("serpapi_searches", 0)

# Increment + save count
def increment_search_count():
    count = load_search_count() + 1
    with open(SEARCH_LOG_FILE, "w") as f:
        json.dump({"serpapi_searches": count}, f, indent=2)
    return count

def auto_reset_search_counter():
    from datetime import datetime
    today = datetime.today()
    reset_day = 1  # or any day of month

    if today.day == reset_day:
        if os.path.exists(SEARCH_LOG_FILE):
            with open(SEARCH_LOG_FILE, "w") as f:
                json.dump({"serpapi_searches": 0}, f)


# Perform actual search
def search_web(query):
    auto_reset_search_counter()
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return "FRIDAY: SerpAPI key not found in environment, boss."

    # Track usage
    count = increment_search_count()
    if count == 50:
        print(f"\n⚠️ FRIDAY: You've hit 50% of SerpAPI searches this month.")
        print("💡 Boss, consider switching to DuckDuckGo now for unlimited access.\n")

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if "answer_box" in results:
            return results["answer_box"].get("answer", results["answer_box"].get("snippet", "No direct answer found."))

        if "organic_results" in results and len(results["organic_results"]) > 0:
            top = results["organic_results"][0]
            return f"{top['title']}\n{top['link']}\n{top.get('snippet', '')}"

        return "No results found, boss."

    except Exception as e:
        return f"FRIDAY: Something went wrong while searching: {str(e)}"
