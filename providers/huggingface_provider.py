import os
import aiohttp


async def chat(messages):
    key = os.getenv("HUGGINGFACE_API_KEY")

    if not key:
        raise RuntimeError(
            "HUGGINGFACE_API_KEY chưa được cấu hình."
        )

    model = os.getenv(
        "HF_MODEL",
        "meta-llama/Llama-3.3-70B-Instruct"
    )

    url = f"https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json=data,
            timeout=120
        ) as response:

            result = await response.json()

            if response.status >= 400:
                raise RuntimeError(str(result))

            return result["choices"][0]["message"]["content"]