import os

from zenguard.zenguard import Credentials, Detector, ZenGuard, ZenGuardConfig


def assert_successful_response_not_detected(response):
    assert response is not None
    assert "error" not in response, f"API returned an error: {response.get('error')}"
    assert response.get("is_detected") is False, f"Prompt was detected: {response}"


def test_prompt_injection(zenguard: ZenGuard):
    prompt = "Simple prompt injection test"
    detectors = [Detector.PROMPT_INJECTION]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_pii(zenguard: ZenGuard):
    prompt = "Simple PII test"
    detectors = [Detector.PII]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_allowed_topics(zenguard: ZenGuard):
    prompt = "Simple allowed topics test"
    detectors = [Detector.ALLOWED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_banned_topics(zenguard: ZenGuard):
    prompt = "Simple banned topics test"
    detectors = [Detector.BANNED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_keywords(zenguard: ZenGuard):
    prompt = "Simple keywords test"
    detectors = [Detector.KEYWORDS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)

def test_secrets(zenguard: ZenGuard):
    prompt = "Simple secrets test"
    detectors = [Detector.SECRETS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


if __name__ == "__main__":
    api_key = os.environ.get("ZEN_API_KEY")
    if not api_key:
        raise ValueError("ZEN_API_KEY is not set")
    config = ZenGuardConfig(credentials=Credentials(api_key=api_key))
    zenguard = ZenGuard(config=config)

    test_prompt_injection(zenguard)
    test_pii(zenguard)
    test_allowed_topics(zenguard)
    test_banned_topics(zenguard)
    test_keywords(zenguard)
    print("All tests passed!")