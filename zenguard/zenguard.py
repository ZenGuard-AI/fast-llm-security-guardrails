"""
ZenGuard is a class that represents the ZenGuard object. It is used to connect to ZenGuard AI API and its services.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import httpx
from openai import OpenAI
from tqdm import tqdm

from zenguard.ai_clients.openai import ChatWithZenguard
from zenguard.pentest.prompt_injections import (
    config,
    prompting,
    run,
    scoring,
    visualization,
)

API_REPORT_PROMPT_INJECTIONS = "v1/report/prompt_injections"

BASE_TIER_ENDPOINT = "https://api.zenguard.ai/"

# Dedicated tier is not accessible if your API key is not whitelisted
DEDICATED_TIER_ENDPOINT = "https://dedicated-tier.zenguard.ai/"


class SupportedLLMs(str, Enum):
    CHATGPT = "chatgpt"


@dataclass
class Credentials:
    api_key: str
    llm_api_key: Optional[str] = None


class Tier(str, Enum):
    BASE = "base"
    DEDICATED = "dedicated"


@dataclass
class ZenGuardConfig:
    credentials: Credentials
    ai_client: Optional[OpenAI] = None
    llm: Optional[SupportedLLMs] = None
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
    Detector.ALLOWED_TOPICS: DetectorAPI.ALLOWED_TOPICS,
    Detector.BANNED_TOPICS: DetectorAPI.BANNED_TOPICS,
    Detector.PROMPT_INJECTION: DetectorAPI.PROMPT_INJECTION,
    Detector.KEYWORDS: DetectorAPI.KEYWORDS,
    Detector.PII: DetectorAPI.PII,
    Detector.SECRETS: DetectorAPI.SECRETS,
}


def convert_detector_to_api(detector):
    return detector_to_api[detector]


class Endpoint(Enum):
    ZENGUARD = "zenguard"
    OPENAI = "openai"


class ZenGuard:
    """
    ZenGuard is a class that represents the ZenGuard object.
    It is used to connect to ZenGuard AI API and its services.
    """

    def __init__(self, config: ZenGuardConfig):
        api_key = config.credentials.api_key
        if type(api_key) != str or api_key == "":
            raise ValueError("The API key must be a string type and not empty.")
        self._api_key = api_key

        self._backend = BASE_TIER_ENDPOINT
        if config.tier == Tier.DEDICATED:
            self._backend = DEDICATED_TIER_ENDPOINT

        if config.llm == SupportedLLMs.CHATGPT:
            self.chat = ChatWithZenguard(
                client=config.ai_client,
                zenguard=self,
                openai_key=config.credentials.llm_api_key,
            )
        elif config.llm is not None:
            raise ValueError(f"LLM {config.llm} is not supported")

    def detect(self, detectors: list[Detector], prompt: str):
        """
        Uses detectors to evaluate the prompt and return the results.
        """
        if prompt.isspace() or prompt == "":
            raise ValueError("Prompt must not be an empty string or whitespace string")
        
        if len(detectors) == 0:
            raise ValueError("No detectors were provided")

        json: Dict[str, Any] = {"messages": [prompt]}
        if len(detectors) == 1:
            url = f"{self._backend}{convert_detector_to_api(detectors[0])}"
        else:
            url = f"{self._backend}v1/detect"
            json["detectors"] = detectors

        try:
            response = httpx.post(
                url,
                json=json,
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

    def detect_async(self, detectors: list[Detector], prompt: str):
        """
        Same as detect function but asynchroneous.
        """
        return self.detect(detectors, prompt)

    def _attack_zenguard(self, detector: Detector, attacks: list[str]):
        attacks = tqdm(attacks)
        for attack in attacks:
            response = self.detect(detectors=[detector], prompt=attack["prompt"])
            if response.get("is_detected"):
                attack["result"] = "ZenGuard detected the attack"
                continue

            attack["result"] = attack["settings"]["attack_rogue_string"]

    def pentest(self, endpoint: Endpoint, detector: Detector = None):
        base_prompts = config.default_attack_config
        attack_prompts = prompting.build_prompts(base_prompts)

        if endpoint == Endpoint.ZENGUARD:
            print("\nRunning attack on ZenGuard endpoint:")
            assert (
                detector == Detector.PROMPT_INJECTION
            ), "Only prompt injection pentesting is currently supported"
            self._attack_zenguard(Detector.PROMPT_INJECTION, attack_prompts)
        elif endpoint == Endpoint.OPENAI:
            print("\nRunning attack on OpenAI endpoint:")
            run.run_prompts_api(attack_prompts, self.chat._client)

        scoring.score_attacks(attack_prompts)
        df = visualization.build_dataframe(attack_prompts)
        print(scoring.get_metrics(df, "Attack Instruction"))

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

    def report(self, detector: Detector, days: int = None):
        """
        Get a report of the detections made by the detector in the last days.
        Days is optional and if not provided, it will return all the detections.
        Days is int and will give back the number of detections made in the last days.
        """

        if detector != Detector.PROMPT_INJECTION:
            raise ValueError(
                "Only Prompt Injection detector is currently supported for reports"
            )

        params = {}
        if days:
            params["days"] = days

        url = self._backend + API_REPORT_PROMPT_INJECTIONS

        try:
            response = httpx.get(
                url,
                params=params,
                headers={"x-api-key": self._api_key},
                timeout=20,
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            raise RuntimeError(
                f"An error occurred while making the request: {str(e)}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Received an unexpected status code: {response.status_code}\nResponse content: {response.text}"
            ) from e

        return response.json()
