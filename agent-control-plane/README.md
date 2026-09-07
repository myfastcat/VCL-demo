# Agent Control Plane — Customer CI Demo

This directory imitates a customer repository using ACP the way it is intended to be used: **as an automatic CI gate**, not as a collection of commands developers run by hand.

## The customer story

The simulated company has a customer-support agent. Its normal tests exercise actions such as `lookup_customer` and `send_email`.

The customer configures ACP once:

- `.acp/authority.json` says which actions are `ALLOW`, `REQUIRE_APPROVAL`, or `DENY`;
- `.acp/config.json` tells ACP where traces and committed incident rules live;
- CI runs the existing agent tests and then the ACP gate.

After that, the developer's normal action is simply to push code/open a PR. CI does the ACP work automatically.

## What CI automatically does

For every change, the acceptance flow runs the customer's ordinary tests and then ACP:

```text
Code change / pull request
        ↓
Customer's existing agent tests
        ↓
Tool-call trace captured/discovered
        ↓
ACP authority check
        +
ACP committed incident-regression check
        ↓
PASS or CI BLOCKED
```

The demo proves three customer-visible outcomes.

### Normal change → CI passes

The agent calls `lookup_customer` and `send_email`. Both are allowed. Application tests pass and ACP passes.

### Authority violation → CI blocks the PR

A code change makes the agent call `delete_customer`. The ordinary application test deliberately remains green, but `.acp/authority.json` marks that action `DENY`. ACP sees the current run's tool calls and fails the gate.

### Historical incident returns → CI blocks the PR

The company previously had a duplicate-email incident. `send_email` itself remains allowed, but the durable incident invariant says it may occur at most once for this regression scenario. When a later code change makes the current run send the email twice, the ordinary application test can remain green while ACP fails the incident-regression gate.

The historical incident is evidence, not a permanently failing trace. CI evaluates its invariant against the **current run's observed behavior**, so fixed code passes and recurrence fails.

## What the customer configures vs. what ACP owns

The customer makes business decisions: the authority boundary and, after a real incident, the invariant that should hold in the future. ACP owns the repetitive technical work in CI: trace capture/discovery, authority evaluation, incident-rule discovery, current-run regression evaluation, exit semantics and build blocking.

A production incident currently enters ACP from a redacted trace exported from the customer's existing logging/observability system. Automatic production-observability ingestion is not yet part of ACP.

## Demo files

- `customer_agent.py` — simulated customer agent/tool code.
- `tests/test_customer_agent.py` — ordinary customer application tests.
- `.acp/authority.json` — customer business authority boundary.
- `.acp/config.json` — ACP CI configuration.
- `incidents/raw-duplicate-email.json` — example historical production incident evidence.
- `.acp/incidents/` — durable incident regression rules used automatically by CI.
- `demo.sh` — acceptance harness that proves the CI behavior, including expected blocking cases.
- `.github/workflows/acp-demo.yml` — customer-shaped automated acceptance workflow.

## Acceptance

The repository workflow runs the full customer-shaped scenario automatically on push/pull request. It installs ACP from `myfastcat/VCL` main at runtime and verifies safe behavior, authority blocking, fixed incident behavior, and recurrence blocking. ACP is customer-demo `VERIFIED` only when this workflow passes in addition to ACP's own product CI.
