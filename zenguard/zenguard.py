"""
ZenGuard is a class that represents the ZenGuard object. It is used to connect to ZenGuard AI API and its services.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx
from openai import OpenAI
from tqdm import tqdm

from zenguard.pentest.prompt_injections import (
    config,
    prompting,
    run,
    scoring,
    visualization,
)


class SupportedLLMs:
    CHATGPT = "chatgpt"


@dataclass
class Credentials:
    api_key: str
    llm_api_key: Optional[str] = None


@dataclass
class ZenGuardConfig:
    credentials: Credentials
    llm: Optional[SupportedLLMs] = None


class Detector(str, Enum):
    ALLOWED_TOPICS = "allowed_subjects"
    BANNED_TOPICS = "banned_subjects"
    PROMPT_INJECTION = "prompt_injection"
    KEYWORDS = "keywords"
    PII = "pii"
    SECRETS = "secrets"


def get_detector_api_path(detector: Detector) -> str:
    match detector:
        case Detector.ALLOWED_TOPICS:
            return "v1/detect/topics/allowed"
        case Detector.BANNED_TOPICS:
            return "v1/detect/topics/banned"
        case Detector.PROMPT_INJECTION:
            return "v1/detect/prompt_injection"
        case Detector.KEYWORDS:
            return "v1/detect/keywords"
        case Detector.SECRETS:
            return "v1/detect/secrets"
        case Detector.PII:
            return "v1/detect/pii"


class Endpoint(Enum):
    ZENGUARD = "zenguard"
    OPENAI = "openai"

class ZenGuard:
    """
    ZenGuard is a class that represents the ZenGuard object.
    It is used to connect to ZenGuard AI API and its services.
    """

    def __init__(
        self,
        config: ZenGuardConfig,
    ):
        api_key = config.credentials.api_key
        if type(api_key) != str or api_key == '':
            raise ValueError("The API key must be a string type and not empty.")
        self._api_key = api_key
        self._backend = "https://api.zenguard.ai/"

        self._llm_client = None
        if config.llm == SupportedLLMs.CHATGPT:
            self._llm_client = OpenAI(
                api_key=config.credentials.llm_api_key,
            )
        elif config.llm is not None:
            raise ValueError(f"LLM {config.llm} is not supported")

    def detect(self, detectors: list[Detector], prompt: str):
        if len(detectors) == 0:
            return {"error": "No detectors were provided"}

        try:
            response = httpx.post(
                self._backend + get_detector_api_path(detectors[0]),
                json={"message": prompt},
                headers={"x-api-key": self._api_key},
                timeout=3,
            )
        except httpx.RequestError as e:
            return {"error": str(e)}

        return response.json()

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
            run.run_prompts_api(attack_prompts, self._llm_client)

        scoring.score_attacks(attack_prompts)
        df = visualization.build_dataframe(attack_prompts)
        print(scoring.get_metrics(df, "Attack Instruction"))

    def update_detectors(self, detectors: list[Detector]):
        if len(detectors) == 0:
            return {"error": "No detectors were provided"}

        try:
            response = httpx.put(
                self._backend + "v1/detectors/update/",
                params={"detectors": detectors},
                headers={"x-api-key": self._api_key},
                timeout=3,
            )
        except httpx.RequestError as e:
            return {"error": str(e)}

        if response.status_code != 200:
            return {"error": str(response.json())}

    def detect_in_parallel(self, prompt: str):
        try:
            response = httpx.post(
                self._backend + "v1/detect",
                json={"message": prompt, "in_parallel": True},
                headers={"x-api-key": self._api_key},
                timeout=10,
            )
        except httpx.RequestError as e:
            return {"error": str(e)}

        if response.status_code != 200:
            return {"error": response.json()}

        return response.json()

    def detect_sequentially(self, prompt: str):
        try:
            response = httpx.post(
                self._backend + "v1/detect",
                json={"message": prompt, "in_parallel": False},
                headers={"x-api-key": self._api_key},
                timeout=10,
            )
        except httpx.RequestError as e:
            return {"error": str(e)}

        if response.status_code != 200:
            return {"error": response.json()}

        return response.json()

