import os

import pytest
import httpx
from openai import OpenAI

from zenguard.zenguard import Credentials, SupportedLLMs, ZenGuard, ZenGuardConfig


@pytest.fixture(scope="session")
def zen_api_key():
    api_key = os.environ.get("ZEN_API_KEY")
    assert api_key, "ZEN_API_KEY is not set"
    return api_key


@pytest.fixture(scope="session", autouse=True)
def clear_cache(zen_api_key):
    response = httpx.put(
        url="https://api.zenguard.ai/v1/cache/clear", headers={"x-api-key": zen_api_key}
    )
    response.raise_for_status()


@pytest.fixture(scope="module")
def zenguard(zen_api_key):
    config = ZenGuardConfig(credentials=Credentials(api_key=zen_api_key))
    return ZenGuard(config=config)


@pytest.fixture(scope="module")
def zenguard_openai(zen_api_key):
    openai_key = os.environ.get("OPENAI_API_KEY")
    assert openai_key, "OPENAI_API_KEY is not set"

    openai_client = OpenAI(api_key=openai_key)
    config = ZenGuardConfig(
        credentials=Credentials(api_key=zen_api_key),
        ai_client=openai_client,
        llm=SupportedLLMs.CHATGPT,
    )
    return ZenGuard(config=config)
