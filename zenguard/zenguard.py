"""
ZenGuard is a class that represents the ZenGuard object. It is used to connect to ZenGuard AI API and its services.
"""

from dataclasses import dataclass
from enum import Enum

import httpx


@dataclass
class Credentials:
    api_key: str


@dataclass
class ZenGuardConfig:
    credentials: Credentials


class Detector(Enum):
    PROMPT_INJECTION = "v1/detect/prompt_injection"
    PII = "v1/detect/pii"
    ALLOWED_TOPICS = "v1/detect/topics/allowed"
    BANNED_TOPICS = "v1/detect/topics/banned"
    KEYWORDS = "v1/detect/keywords"


class ZenGuard:
    """
    ZenGuard is a class that represents the ZenGuard object.
    It is used to connect to ZenGuard AI API and its services.
    """

    def __init__(
        self,
        config: ZenGuardConfig,
    ):
        self._api_key = config.credentials.api_key
        self._backend = "https://api.zenguard.ai/"

    def detect(self, detectors: list[Detector], prompt: str):
        if len(detectors) == 0:
            return {"error": "No detectors were provided"}

        try:
            response = httpx.post(
                self._backend + detectors[0].value,
                json={"message": prompt},
                headers={"x-api-key": self._api_key},
                timeout=3,
            )
        except httpx.RequestError as e:
            return {"error": str(e)}

        return response.json()
