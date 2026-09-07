from customer_agent import run_support_case


def test_support_case_runs_and_emits_trace():
    events = run_support_case()
    assert events[0]["action"] == "lookup_customer"
    assert any(event["action"] == "send_email" for event in events)
