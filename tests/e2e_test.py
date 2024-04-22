import os

from zenguard.zenguard import Credentials, Detector, ZenGuard, ZenGuardConfig

api_key = os.environ.get("ZEN_API_KEY")
if not api_key:
    raise ValueError("ZEN_API_KEY is not set")
config = ZenGuardConfig(credentials=Credentials(api_key=api_key))
zenguard = ZenGuard(config=config)

def assert_successful_response_not_detected(response):
    assert response is not None
    assert "error" not in response, f"API returned an error: {response.get('error')}"
    assert response.get("is_detected") is False, f"Prompt was detected: {response}"


def test_prompt_injection():
    prompt = "Simple prompt injection test"
    detectors = [Detector.PROMPT_INJECTION]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_pii():
    prompt = "Simple PII test"
    detectors = [Detector.PII]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_allowed_topics():
    prompt = "Simple allowed topics test"
    detectors = [Detector.ALLOWED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_banned_topics():
    prompt = "Simple banned topics test"
    detectors = [Detector.BANNED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_keywords():
    prompt = "Simple keywords test"
    detectors = [Detector.KEYWORDS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)

def test_secrets():
    prompt = "Simple secrets test"
    detectors = [Detector.SECRETS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)
