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
    SECRETS = "v1/detect/secrets"


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
        ai_client: Optional[OpenAI] = None
    ):
        self._api_key = config.credentials.api_key
        self._backend = "https://api.zenguard.ai/"

        self._llm_client = None
        if ai_client is not None and isinstance(ai_client, OpenAI):
            self._llm_client = ai_client
        elif ai_client is not None:
            raise ValueError("Currently only ChatGPT is supported")

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
    
    def detect_and_send_prompt(self, detectors: list[Detector], prompt: str):
        try:
            detected_response = self.detect(detectors, prompt)
            if "error" in detected_response:
                return detected_response
            llm_response = self._llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": detected_response["sanitized_message"]}]
            )
            return {
                "detect_response": detected_response,
                "llm_response": llm_response
            }
        except httpx.RequestError as e:
            return {"error": str(e)}

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
