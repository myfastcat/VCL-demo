# Agent Control Plane — Customer Demo

This directory is a small simulated customer repository for demonstrating ACP to a buyer or engineering team.

The sample agent can look up a customer and send a retention email. A hidden demo switch makes it also call `delete_customer`; ACP should allow the normal flow and block the simulated authority violation.

## Run the demo

```bash
cd agent-control-plane
bash demo.sh
```

Expected story:

1. the normal customer-support flow emits tool-call trace data and `acp check` passes;
2. the demo injects `delete_customer` without changing the unit-test expectation;
3. the application test still passes, but ACP detects the denied action and exits `2`;
4. the script treats that ACP failure as the successful demo outcome.

## Files a customer would recognize

- `customer_agent.py` — simulated application/tool code.
- `tests/test_customer_agent.py` — ordinary application test that emits a trace artifact.
- `.acp/authority.json` — business authority boundary: lookup/email allowed, customer deletion denied.
- `.acp/config.json` — tells ACP where the customer trace is located.
- `demo.sh` — repeatable sales/demo path.

## What this proves

The demo is intentionally customer-shaped rather than an ACP internal unit test. It demonstrates that an application test can remain green while ACP independently fails the build because the observed agent action crossed an explicit authority boundary.

## Current scope of this demo

This first customer demo verifies the authority-gate path. Incident-regression is not presented here as customer-verified until its end-to-end replay semantics are separately exercised by a customer-shaped reproduction scenario.
