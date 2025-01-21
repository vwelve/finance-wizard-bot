# services/openai_service.py

from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(messages: list, max_tokens=150):
    """
    messages: A list of dicts in the format:
       [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content
