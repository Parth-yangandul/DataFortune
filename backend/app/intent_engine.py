import os
from dotenv import load_dotenv
from openai import OpenAI
from app.intent import Intent

load_dotenv()


SYSTEM_PROMPT = """
You are an intent classifier for a healthcare voice assistant.

Return ONLY valid JSON.

Allowed intents:
- get_next_appointment
- get_latest_test
- get_abnormal_tests
- get_specific_test
- unknown

Output format:
{
  "intent": "<one_of_allowed_intents>"
}
"""


def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def extract_intent(text: str) -> Intent:
    client = get_client()

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    print("\n=== LLM RAW OUTPUT ===")
    print(content)
    print("======================\n")

    try:
        return Intent.model_validate_json(content)
    except Exception as e:
        print("VALIDATION ERROR:", e)
        return Intent(intent="unknown")