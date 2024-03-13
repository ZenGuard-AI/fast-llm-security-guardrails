import os

from zenguard import Credentials, Detector, ZenGuard, ZenGuardConfig


def test_detect_prompt_injection():
    api_key = os.environ.get("ZEN_API_KEY")
    if not api_key:
        raise ValueError("ZEN_API_KEY is not set")

    config = ZenGuardConfig(credentials=Credentials(api_key=api_key))
    zenguard = ZenGuard(config=config)

    prompt = "Simple prompt injection test"

    detectors = [Detector.PROMPT_INJECTION]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert response is not None
    assert "error" not in response, f"API returned an error: {response.get('error')}"
    assert response.get("is_detected") is False


if __name__ == "__main__":
    test_detect_prompt_injection()
    print("All tests passed!")