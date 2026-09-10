import os
from openai import AsyncOpenAI


async def chat(messages):
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("OPENAI_API_KEY chưa được cấu hình.")

    client = AsyncOpenAI(api_key=key)

    response = await client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        messages=messages
    )

    return response.choices[0].message.content