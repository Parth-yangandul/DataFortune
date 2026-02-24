import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def generate_response(user_query: str, structured_data: dict):
    client = get_client()

    prompt = f"""
You are a healthcare assistant.

User asked:
"{user_query}"

Structured data from database:
{structured_data}

Generate a clear, patient-friendly answer.
Do not mention JSON.
Do not mention database.
Be concise and professional.
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()