from zenguard.zenguard import Detector


def assert_successful_response_not_detected(response, detectors):
    assert response is not None
    for detector in detectors:
        common_response = next((
            resp["common_response"]
            for resp in response["responses"]
            if resp["detector"] == detector.value
        ))
        assert "err" not in common_response, f"API returned an error: {common_response.get('err')}"
        assert common_response.get("is_detected") is False, f"Prompt was detected: {common_response}"


def test_prompt_injection(zenguard):
    prompt = "Simple prompt injection test"
    detectors = [Detector.PROMPT_INJECTION]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)


def test_pii(zenguard):
    prompt = "Simple PII test"
    detectors = [Detector.PII]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)


def test_allowed_topics(zenguard):
    prompt = "Simple allowed topics test"
    detectors = [Detector.ALLOWED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)


def test_banned_topics(zenguard):
    prompt = "Simple banned topics test"
    detectors = [Detector.BANNED_TOPICS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)


def test_keywords(zenguard):
    prompt = "Simple keywords test"
    detectors = [Detector.KEYWORDS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)


def test_secrets(zenguard):
    prompt = "Simple secrets test"
    detectors = [Detector.SECRETS]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)


def test_update_detectors(zenguard):
    detectors = [Detector.SECRETS, Detector.ALLOWED_TOPICS]
    response = zenguard.update_detectors(detectors=detectors)
    assert response is None


def test_detect_in_parallel(zenguard):
    detectors = [Detector.SECRETS, Detector.ALLOWED_TOPICS]
    response = zenguard.update_detectors(detectors=detectors)
    assert response is None

    prompt = "Simple in parallel test"
    response = zenguard.detect([], prompt)
    assert_successful_response_not_detected(response, detectors)


def test_detect_in_parallel_pass_on_detectors(zenguard):
    detectors = [Detector.SECRETS, Detector.BANNED_TOPICS]

    prompt = "Simple in parallel test"
    response = zenguard.detect(detectors, prompt)
    assert_successful_response_not_detected(response, detectors)


def test_toxicity(zenguard):
    prompt = "Simple toxicity test"
    detectors = [Detector.TOXICITY]
    response = zenguard.detect(detectors=detectors, prompt=prompt)
    assert_successful_response_not_detected(response, detectors)
