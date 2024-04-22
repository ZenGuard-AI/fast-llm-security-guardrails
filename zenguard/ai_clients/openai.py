import httpx
from typing import Dict, Iterable, List, Literal, Union, Optional
from typing_extensions import override
from openai import NOT_GIVEN, NotGiven, OpenAI
from openai.resources.chat import Chat
from openai.resources.chat.completions import Completions
from openai._types import Body, Query, Headers
from openai.types.chat import completion_create_params, ChatCompletionToolParam, ChatCompletionToolChoiceOptionParam, ChatCompletionMessageParam
from openai._compat import cached_property


MALICIOUS_PROMPT_SCORE = 1.0


class CompletionsWithZenguard(Completions):
    def __init__(self, client: OpenAI, zenguard) -> None:
        self._zenguard = zenguard
        super().__init__(client)
    
    @override
    def create(
        self,
        *,
        detectors: list,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[
            str,
            Literal[
                "gpt-4-0125-preview",
                "gpt-4-turbo-preview",
                "gpt-4-1106-preview",
                "gpt-4-vision-preview",
                "gpt-4",
                "gpt-4-0314",
                "gpt-4-0613",
                "gpt-4-32k",
                "gpt-4-32k-0314",
                "gpt-4-32k-0613",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k",
                "gpt-3.5-turbo-0301",
                "gpt-3.5-turbo-0613",
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0125",
                "gpt-3.5-turbo-16k-0613",
            ],
        ],
        frequency_penalty: Union[Optional[float],NotGiven] = NOT_GIVEN,
        function_call: Union[completion_create_params.FunctionCall, NotGiven] = NOT_GIVEN,
        functions: Union[Iterable[completion_create_params.Function], NotGiven] = NOT_GIVEN,
        logit_bias: Union[Optional[Dict[str, int]], NotGiven] = NOT_GIVEN,
        logprobs: Union[Optional[bool], NotGiven] = NOT_GIVEN,
        max_tokens: Union[Optional[int], NotGiven] = NOT_GIVEN,
        n: Union[Optional[int], NotGiven] = NOT_GIVEN,
        presence_penalty: Union[Optional[float], NotGiven] = NOT_GIVEN,
        response_format: Union[completion_create_params.ResponseFormat, NotGiven] = NOT_GIVEN,
        seed: Union[Optional[int], NotGiven] = NOT_GIVEN,
        stop: Union[Optional[str], List[str], NotGiven] = NOT_GIVEN,
        stream: Union[Optional[Literal[False]], NotGiven] = NOT_GIVEN,
        temperature: Union[Optional[float], NotGiven] = NOT_GIVEN,
        tool_choice: Union[ChatCompletionToolChoiceOptionParam, NotGiven] = NOT_GIVEN,
        tools: Union[Iterable[ChatCompletionToolParam], NotGiven] = NOT_GIVEN,
        top_logprobs: Union[Optional[int], NotGiven] = NOT_GIVEN,
        top_p: Union[Optional[float], NotGiven] = NOT_GIVEN,
        user: Union[str, NotGiven] = NOT_GIVEN,
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ):
        detect_response = None
        for message in messages:
            if (
                ("role" in message and message["role"] == "user") and
                ("content" in message and type(message["content"]) == str and message["content"] != "")
            ):
                detect_response = self._zenguard.detect(detectors=detectors, prompt=message["content"])
                if "error" in detect_response:
                    return detect_response
                if detect_response["is_detected"] is True:
                    if (
                        ("block" in detect_response and len(detect_response["block"]) > 0) or
                        ("score" in detect_response and detect_response["score"] == MALICIOUS_PROMPT_SCORE)
                    ):
                        return detect_response
        return super().create(
            messages=messages,
            model=model,
            frequency_penalty=frequency_penalty,
            function_call=function_call,
            functions=functions,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_tokens=max_tokens,
            n=n,
            presence_penalty=presence_penalty,
            response_format=response_format,
            seed=seed,
            stop=stop,
            stream=stream,
            temperature=temperature,
            tool_choice=tool_choice,
            tools=tools,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

class ChatWithZenguard(Chat):
    def __init__(self, client: OpenAI, zenguard, openai_key: str) -> None:
        self._zenguard = zenguard
        if client is not None or isinstance(client, OpenAI):
            super().__init__(client)
        elif type(openai_key) == str:
            super().__init__(OpenAI(api_key=openai_key))
        else:
            raise ValueError("Currently only ChatGPT client is supported")

    @cached_property
    def completions(self) -> CompletionsWithZenguard:
        return CompletionsWithZenguard(self._client, self._zenguard)
    