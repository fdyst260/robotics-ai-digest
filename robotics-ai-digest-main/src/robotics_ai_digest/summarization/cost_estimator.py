from __future__ import annotations

import tiktoken

DEFAULT_EXPECTED_OUTPUT_TOKENS = 220
DEFAULT_PRICE_PER_1K_TOKENS = 0.002

# Approximate blended $ / 1K tokens for estimation.
MODEL_PRICE_PER_1K_TOKENS: dict[str, float] = {
    "gpt-4.1-mini": 0.002,
    "gpt-4o-mini": 0.00075,
}


def count_tokens(prompt: str, model: str = "gpt-4.1-mini") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(prompt))


def estimate_api_cost(
    prompt: str,
    model: str = "gpt-4.1-mini",
    expected_output_tokens: int = DEFAULT_EXPECTED_OUTPUT_TOKENS,
) -> float:
    input_tokens = count_tokens(prompt, model=model)
    total_tokens = input_tokens + expected_output_tokens
    price_per_1k = MODEL_PRICE_PER_1K_TOKENS.get(model, DEFAULT_PRICE_PER_1K_TOKENS)
    return (total_tokens / 1000) * price_per_1k

