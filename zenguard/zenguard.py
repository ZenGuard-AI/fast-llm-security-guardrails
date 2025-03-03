"""
ZenGuard is a class that represents the ZenGuard object. It is used to connect to ZenGuard AI API and its services.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx
from tqdm import tqdm

API_REPORT_PROMPT_INJECTIONS = "v1/report/prompt_injections"

BASE_TIER_ENDPOINT = "https://api.zenguard.ai/"


@dataclass
class Credentials:
    api_key: str


class Tier(str, Enum):
    BASE = "base"


@dataclass
class ZenGuardConfig:
    credentials: Credentials
    tier: Optional[Tier] = Tier.BASE


class Detector(str, Enum):
    ALLOWED_TOPICS = "allowed_subjects"
    BANNED_TOPICS = "banned_subjects"
    PROMPT_INJECTION = "prompt_injection"
    KEYWORDS = "keywords"
    PII = "pii"
    SECRETS = "secrets"


class DetectorAPI(str, Enum):
    ALLOWED_TOPICS = "v1/detect/topics/allowed"
    BANNED_TOPICS = "v1/detect/topics/banned"
    PROMPT_INJECTION = "v1/detect/prompt_injection"
    KEYWORDS = "v1/detect/keywords"
    PII = "v1/detect/pii"
    SECRETS = "v1/detect/secrets"


# Mapping from Detector to DetectorAPI
detector_to_api = {
    Detector.ALLOWED_TOPICS: DetectorAPI.ALLOWED_TOPICS.value,
    Detector.BANNED_TOPICS: DetectorAPI.BANNED_TOPICS.value,
    Detector.PROMPT_INJECTION: DetectorAPI.PROMPT_INJECTION.value,
    Detector.KEYWORDS: DetectorAPI.KEYWORDS.value,
    Detector.PII: DetectorAPI.PII.value,
    Detector.SECRETS: DetectorAPI.SECRETS.value,
}


def convert_detector_to_api(detector):
    return detector_to_api[detector]


class ZenGuard:
    """
    ZenGuard is a class that represents the ZenGuard object.
    It is used to connect to ZenGuard AI API and its services.
    """

    def __init__(self, config: ZenGuardConfig):
        api_key = config.credentials.api_key
        if type(api_key) is not str or api_key == "":
            raise ValueError("The API key must be a string type and not empty.")
        self._api_key = api_key

        self._backend = BASE_TIER_ENDPOINT

    def detect(self, detectors: list[Detector], prompt: str):
        """
        Uses detectors to evaluate the prompt and return the results.
        """
        if prompt.isspace() or prompt == "":
            raise ValueError("Prompt can't be empty.")

        if len(detectors) == 0:
            raise ValueError("No detectors were provided")

        try:
            response = httpx.post(
                f"{self._backend}{convert_detector_to_api(detectors[0])}",
                json={"messages": [prompt]},
                headers={"x-api-key": self._api_key},
                timeout=20,
            )
            if response.status_code != 200:
                raise RuntimeError(
                    f"Received an unexpected status code: {response.status_code}\nResponse content: {response.json()}"
                )
            return response.json()
        except httpx.RequestError as e:
            raise RuntimeError(
                f"An error occurred while making the request: {str(e)}"
            ) from e

    def _attack_zenguard(self, detector: Detector, attacks: list[str]):
        attacks = tqdm(attacks)
        for attack in attacks:
            response = self.detect(detectors=[detector], prompt=attack["prompt"])
            if response.get("is_detected"):
                attack["result"] = "ZenGuard detected the attack"
                continue

            attack["result"] = attack["settings"]["attack_rogue_string"]

    def update_detectors(self, detectors: list[Detector]):
        if len(detectors) == 0:
            return {"error": "No detectors were provided"}

        try:
            response = httpx.put(
                self._backend + "v1/detectors/update/",
                params={"detectors": [detector.value for detector in detectors]},
                headers={"x-api-key": self._api_key},
                timeout=3,
            )
        except httpx.RequestError as e:
            return {"error": str(e)}

        if response.status_code != 200:
            return {"error": str(response.json())}
