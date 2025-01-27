import aiohttp

import os

from config import WATT_API_KEY
from util import get_logger

logger = get_logger(__name__)


async def search_web(prompt):
    data = {
        "model": "wp-watt-3.52-16k",
        "content": prompt
    }
    headers = {
        "Authorization": f"Bearer {WATT_API_KEY}",
    }

    logger.info(f"Making a call to WATT_API with prompt: {prompt}")
    api_url = "https://beta.webpilotai.com/api/v1/watt/"
    async with aiohttp.ClientSession() as session:
        logger.info(f"Calling {api_url} Data: {data} and Headers: {headers}.")
        rsp = await session.post(
            api_url,
            headers=headers,
            json=data
        )

    content = (await rsp.json())

    return content["content"]
