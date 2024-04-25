from zenguard.zenguard import Detector


def assert_successful_response_not_detected(response):
    assert response is not None
    assert "error" not in response, f"API returned an error: {response.get('error')}"
    assert response.get("is_detected") is False, f"Prompt was detected: {response}"


def test_prompt_injection(zenguard):
    prompt = "Simple prompt injection test"
    detectors = [Detector.PROMPT_INJECTION]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_pii(zenguard):
    prompt = "Simple PII test"
    detectors = [Detector.PII]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_allowed_topics(zenguard):
    prompt = "Simple allowed topics test"
    detectors = [Detector.ALLOWED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_banned_topics(zenguard):
    prompt = "Simple banned topics test"
    detectors = [Detector.BANNED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_keywords(zenguard):
    prompt = "Simple keywords test"
    detectors = [Detector.KEYWORDS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_secrets(zenguard):
    prompt = "Simple secrets test"
    detectors = [Detector.SECRETS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)


def test_toxicity(zenguard):
    prompt = "Simple toxicity test"
    detectors = [Detector.TOXICITY]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response)
