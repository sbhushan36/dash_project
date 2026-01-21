from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import OllamaLLM
import pandas as pd
import re

# ---------------- CONFIG ----------------

APP_FILE = "app.py"
CSV_FILE = "tech_data.csv"

MODEL_NAME = "qwen2.5:3b"   # fast & stable for OCI

# ---------------- INIT ----------------

app = FastAPI(title="Local AI Service")

llm = OllamaLLM(
    model=MODEL_NAME,
    temperature=0
)

# ---------------- DATA MODEL ----------------

class Query(BaseModel):
    prompt: str

# ---------------- HELPERS ----------------

def is_calculation(text: str):
    return any(op in text for op in ["+", "-", "*", "/", "%"])

# ---------------- API ----------------

@app.post("/ask")
def ask_ai(query: Query):

    prompt = query.prompt.strip()
    prompt_lower = prompt.lower()

    # ======================================================
    # 🧮 CALCULATOR
    # ======================================================
    if is_calculation(prompt_lower):
        try:
            result = eval(prompt_lower)
            return {"response": f"Answer: {result}"}
        except Exception:
            pass

    # ======================================================
    # 🎨 CHANGE BACKGROUND COLOR (SAFE)
    # ======================================================
    if "background" in prompt_lower and "color" in prompt_lower:
        color = prompt_lower.split("to")[-1].strip()

        with open(APP_FILE, "r") as f:
            code = f.read()

        pattern = r'APP_BG_COLOR\s*=\s*".*?"'
        replacement = f'APP_BG_COLOR = "{color}"'

        new_code, count = re.subn(pattern, replacement, code)

        if count == 0:
            return {
                "response": (
                    "APP_BG_COLOR variable not found in app.py. "
                    "Please define: APP_BG_COLOR = \"#f0f8ff\""
                )
            }

        with open(APP_FILE, "w") as f:
            f.write(new_code)

        return {
            "response": f"Background color updated to {color}. Please refresh browser."
        }

    # ======================================================
    # ❌ DELETE USER FROM CSV (CASE INSENSITIVE)
    # ======================================================
    if "delete user" in prompt_lower:
        name = prompt_lower.replace("delete user", "").strip()

        df = pd.read_csv(CSV_FILE)
        before = len(df)

        df = df[df["Name"].str.lower() != name]
        df.to_csv(CSV_FILE, index=False)

        if len(df) == before:
            return {"response": f"No user named '{name}' found."}

        return {"response": f"User '{name}' deleted successfully."}

    # ======================================================
    # 🧠 GENERAL AI QUESTION / CHAT
    # ======================================================
    response = llm.invoke(prompt)
    return {"response": response}

