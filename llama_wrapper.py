import subprocess

MODEL = "llama3"  # or "llama3:70b" if you go big later

def query_llama(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL, prompt],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"[LLaMA Error] {e}"
