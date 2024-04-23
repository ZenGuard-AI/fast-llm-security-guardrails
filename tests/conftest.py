import os

import pytest
from openai import OpenAI

from zenguard.zenguard import Credentials, SupportedLLMs, ZenGuard, ZenGuardConfig


@pytest.fixture(scope="session", autouse=True)
def zenguard():
    api_key = os.environ.get("ZEN_API_KEY")
    assert api_key, "ZEN_API_KEY is not set"
    config = ZenGuardConfig(credentials=Credentials(api_key=api_key))
    return ZenGuard(config=config)


@pytest.fixture(scope="session", autouse=True)
def zenguard_openai():
    api_key = os.environ.get("ZEN_API_KEY")
    assert api_key, "ZEN_API_KEY is not set"

    openai_key = os.environ.get("OPENAI_API_KEY")
    assert openai_key, "OPENAI_API_KEY is not set"

    openai_client = OpenAI(api_key=openai_key)
    config = ZenGuardConfig(
        credentials=Credentials(api_key=api_key),
        ai_client=openai_client,
        llm=SupportedLLMs.CHATGPT,
    )
    return ZenGuard(config=config)