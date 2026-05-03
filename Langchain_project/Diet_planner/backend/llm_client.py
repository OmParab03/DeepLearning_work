from http import client

from groq import Groq
from dotenv import dotenv_values
import json

env_vars = dotenv_values(".env")
GroqAPIkey = env_vars.get("GroqAPIkey") 
re_generator = env_vars.get("llm_2_api_key")

client1 = Groq(api_key=GroqAPIkey)

def generate_diet(prompt):
    response = client1.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ---------------- MODIFY EXISTING PLAN ---------------- #


def modify_diet(base_plan, user_request):

    # ✅ convert to CLEAN JSON string
    base_plan_json = json.dumps(base_plan, indent=2)

    prompt = f"""
You are a STRICT JSON editor.

You MUST modify the given JSON WITHOUT breaking structure.

================ INPUT PLAN (JSON) ================
{base_plan_json}

================ USER REQUEST =====================
{user_request}

================ STRICT RULES =====================

- DO NOT change structure
- DO NOT add/remove days
- DO NOT change number of meals
- DO NOT change meal times
- DO NOT reorder anything
- DO NOT rename keys

- ONLY change:
  → "food"
  → "calories" (if needed)

- If removing something:
  → replace with similar alternative

Examples:
- coconut water → buttermilk
- fried food → grilled version

================ CRITICAL =================

- Output MUST be valid JSON
- Output MUST match EXACT structure of input
- Same number of days
- Same meals per day
- Same time values

If modification is not possible:
→ RETURN ORIGINAL JSON

================ OUTPUT =================

Return ONLY JSON.
No explanation.
"""
    client2= Groq(api_key=re_generator)

    response = client2.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a strict JSON editor. Never break structure."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2 
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    prompt = "hiii"
    print(generate_diet(prompt))

