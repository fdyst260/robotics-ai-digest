from robotics_ai_digest.summarization.cost_estimator import count_tokens, estimate_api_cost


def test_estimate_api_cost_short_prompt_returns_positive_value():
    prompt = "Robotics article about autonomous navigation."
    estimated = estimate_api_cost(prompt, model="gpt-4.1-mini", expected_output_tokens=100)

    assert estimated > 0


def test_count_tokens_is_deterministic_for_same_prompt():
    prompt = "Short prompt for token test."
    t1 = count_tokens(prompt, model="gpt-4.1-mini")
    t2 = count_tokens(prompt, model="gpt-4.1-mini")

    assert t1 == t2
    assert t1 > 0

