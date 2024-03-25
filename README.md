[![ZenGuard SDK CI](https://github.com/ZenGuard-AI/zenguard-ai/actions/workflows/github-actions.yaml/badge.svg)](https://github.com/ZenGuard-AI/zenguard-ai/actions/workflows/github-actions.yaml) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://img.shields.io/pypi/v/zenguard)](https://pypi.org/project/zenguard/)

![image](https://github.com/ZenGuard-AI/easy-llm-security/assets/2197820/dd842a17-99b5-4158-a8f5-af8cdebe4f02)


# ZenGuard AI

ZenGuard AI enables AI developers to integrate production-level, low-code LLM (Large Language Model) guardrails into their generative AI applications effortlessly. With ZenGuard AI, ensure your application operates within trusted boundaries, is protected from malicious attacks and maintains user privacy without compromising on performance.

# Features

* **Prompt Injection Detection**: Identifies and mitigates attempts to manipulate, exfiltrate proprietary data and insert malicious content to/from models and RAG systems.
* **Jailbreak Detection**: Identifies and mitigates attempts to manipulate model/app outputs.
* **Personally Identifiable Information (PII) Detection**: Protects user data privacy by detecting and managing sensitive information.
* **Allowed Topics Detection**: Enables your model/app to generate content within specified, permissible topics.
* **Banned Topics Detection**: Prevents the model from producing content on prohibited subjects.
* **Keywords Detection**: Allows filtering and sanitization of your application's requests and responses or content generation based on specific keywords.

# Quick Start
## Installation

Start by installing ZenGuard package:

```shell
pip install zenguard
```

## Getting Started

Jump into our [Quickstart Guide](https://docs.zenguard.ai/start-here/quickstart/) to easily integrate ZenGuard AI into your application.

# ZenGuard Playground

Test the capabilities of ZenGuard AI in our ZenGuard [Playground](https://console.zenguard.ai/chat). It's available to start for free to understand how our guardrails can enhance your GenAI applications.

# Documentation

A more detailed documentation is available at [docs.zenguard.ai](https://docs.zenguard.ai/).


# Pentesting

You can run pentest against both ZenGuard AI and (optionally) ChatGPT.

Clone this repo and install requirements.

Run pentest against ZenGuard AI:

```shell
export ZEN_API_KEY=your-api-key
python tests/pentest.py
```

Run pentest against both ZenGuard AI and ChatGPT:
```shell
export ZEN_API_KEY=your-api-key
export OPENAI_API_KEY=your-openai-api-key
python tests/pentest.py
```


Note that we always are running the pentest against the most up-to-date model. Currently, `gpt-4-0125-preview`



# Support and Contact

[Book a Demo](https://calendly.com/galym-u) or just shoot us an email to hello@zenguard.ai.

---

<p align="center"> Developed with :heart: by https://zenguard.ai/ </p>

---
