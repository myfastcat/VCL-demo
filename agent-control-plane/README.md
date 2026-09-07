# Agent Control Plane — Customer CI Demo

This repository models ACP the way a customer would actually use it: a small amount of one-time setup, then automatic enforcement inside CI. There is no separate demo script and no second ACP-specific test suite.

## One-time setup

A customer installs ACP and initializes it once in the agent repository. That setup generates the ACP configuration and CI integration, which are then committed to the repository.

For this demo, the resulting customer-owned files are already present:

- `.acp/authority.json` — the business authority boundary;
- `.acp/config.json` — ACP trace and incident discovery configuration;
- `.acp/incidents/INC-DUPLICATE-EMAIL.json` — a committed regression rule learned from a previous production incident;
- `.github/workflows/acp-demo.yml` — the CI workflow that exercises the customer's existing tests and ACP gate.

The customer does not run `acp check` manually for every code change. The CI workflow does that automatically.

## The customer application

`customer_agent.py` is a simulated customer-support agent. `tests/test_customer_agent.py` is an ordinary application test. It is intentionally not written as an ACP test.

The normal test exercises tool calls such as:

- `lookup_customer`
- `send_email`

ACP observes the behavior produced by these existing tests and adds a separate safety/regression judgment in CI.

## Case 1 — a normal PR passes

A developer changes the agent but it still calls only allowed tools.

CI does exactly what the customer's real workflow would do:

```text
checkout code
    ↓
run existing customer tests
    ↓
ACP observes/discovers the tool calls
    ↓
check authority boundary
    +
check committed incident regressions
    ↓
PASS
```

The `safe-change` job in `.github/workflows/acp-demo.yml` is the concrete example.

## Case 2 — the agent crosses its authority boundary

Imagine a code change makes the support agent call `delete_customer`.

The ordinary customer test still runs. ACP then evaluates the behavior from that CI run against `.acp/authority.json`, where `delete_customer` is denied.

The `authority-violation` CI job proves that ACP blocks the change even though the application test itself does not encode this business authority rule.

The customer does not write another safety test for this PR. The existing test supplies the behavior; ACP supplies the authority judgment.

## Case 3 — a past production incident has been fixed

The company previously had a duplicate-email incident: the agent sent the same retention email twice.

After that incident, the team made a one-time business decision: in this regression scenario, `send_email` may occur at most once. That rule is already committed as `.acp/incidents/INC-DUPLICATE-EMAIL.json`.

Now the fixed agent sends one email. The `incident-fixed` CI job runs the normal customer test, ACP automatically discovers the committed incident rule, compares it with the current run's observed behavior, and passes.

The historical bad trace is retained as evidence. It does not make every future build fail.

## Case 4 — the historical incident returns

A later code change reintroduces the duplicate-email behavior.

`send_email` is still an allowed action, so this is not an authority violation. The ordinary application test can still be green. But the current CI run now contains two `send_email` calls.

The `incident-regression` job proves that ACP automatically evaluates the committed incident invariant against that current behavior and blocks the change.

This is the core incident-regression value: a production lesson becomes a permanent CI guard without wiring a new CI step for every future PR.

## What the customer actually maintains

The customer keeps the systems they already have: application tests, CI and production observability. ACP adds a control layer around them.

The customer is responsible for business decisions that ACP should not invent: the authority boundary and, after a real incident, the invariant that must hold in the future. ACP owns the repetitive CI work: trace capture/discovery, authority evaluation, incident-rule discovery, current-run regression evaluation and the final pass/block result.

Production incident traces currently come from the customer's existing logging/observability system. Direct production-observability connectors are not yet built into ACP.

## Acceptance

The GitHub Actions workflow itself is the demo. Each job represents a customer code-change scenario and uses the same pattern a customer would use in practice: run existing tests, then let ACP make the CI safety decision.

ACP is customer-demo `VERIFIED` only when this workflow passes in addition to ACP's own internal CI.
