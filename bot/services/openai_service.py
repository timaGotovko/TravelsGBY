from openai import OpenAI
from bot.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def ask_gpt(message_history: list[dict]) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
