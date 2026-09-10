import os
import aiohttp


async def chat(messages):
    key = os.getenv("REPLICATE_API_TOKEN")

    if not key:
        raise RuntimeError(
            "REPLICATE_API_TOKEN chưa được cấu hình."
        )

    model = os.getenv(
        "REPLICATE_MODEL",
        "meta/meta-llama-3.1-405b-instruct"
    )

    url = "https://api.replicate.com/v1/models"

    # Provider này để riêng để sau này thay model
    # theo model Replicate mà bạn chọn.

    raise RuntimeError(
        "Replicate adapter cần chọn chính xác model/version "
        "trước khi bật production."
    )